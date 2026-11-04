#!/usr/bin/env python3
"""
scrape_udemy_courses.py

Tools scraping/automation untuk mengambil informasi kursus dari halaman
Udemy "My Learning" menggunakan Playwright (sync API).

Cara pakai:
    python scrape_udemy_courses.py \
        --url "https://www.udemy.com/home/my-courses/learning/" \
        --output "courses.csv"

Opsi:
    --url         URL halaman My Learning (opsional; bisa pakai UDEMY_URL atau input saat runtime)
    --output      Nama file CSV output (default: courses.csv).
    --max-pages   Batas jumlah halaman pagination (opsional).
    --headless    Jalankan tanpa GUI (default: non-headless).

Alur:
    1. Browser Chromium terbuka (non-headless).
    2. User login manual bila perlu.
    3. User menekan ENTER di terminal setelah daftar kursus terlihat.
    4. Script auto-scroll + scraping tiap halaman, lalu pindah halaman (Next).
    5. Hasil disimpan ke CSV (utf-8-sig) tanpa duplikasi.
"""

import argparse
import csv
import logging
import os
import re
import sys
import time
from typing import Dict, List, Optional, Set

from playwright.sync_api import (
    Page,
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
    Error as PlaywrightError,
)

# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("udemy_scraper")


# --------------------------------------------------------------------------- #
# 1. parse_args
# --------------------------------------------------------------------------- #
def parse_args() -> argparse.Namespace:
    """Parse argumen baris perintah."""
    parser = argparse.ArgumentParser(
        description="Scraper kursus Udemy My Learning (Playwright sync API)."
    )
    parser.add_argument(
        "--url",
        required=False,
        default=None,
        help="URL halaman Udemy My Learning. (opsional; bisa pakai UDEMY_URL atau input saat runtime)",
    )
    parser.add_argument(
        "--output",
        default="courses.csv",
        help="Nama file CSV output (default: courses.csv).",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Batas maksimum jumlah halaman pagination (opsional).",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Jalankan browser dalam mode headless (default: non-headless).",
    )
    return parser.parse_args()


def resolve_target_url(args: argparse.Namespace) -> str:
    """
    Tentukan URL target dari:
      1) --url
      2) env UDEMY_URL
      3) prompt input user
    """
    # 1) dari argumen
    if args.url:
        return args.url.strip()

    # 2) dari env
    env_url = os.environ.get("UDEMY_URL")
    if env_url and env_url.strip():
        return env_url.strip()

    # 3) prompt
    try:
        url = input(
            "Masukkan URL Udemy My Learning (contoh: https://www.udemy.com/home/my-courses/learning/): "
        ).strip()
    except (EOFError, KeyboardInterrupt):
        logger.error("Input URL dibatalkan oleh user. Keluar.")
        sys.exit(1)

    if not url:
        logger.error("URL tidak boleh kosong. Keluar.")
        sys.exit(1)

    return url


# --------------------------------------------------------------------------- #
# 2. wait_for_manual_login
# --------------------------------------------------------------------------- #
def wait_for_manual_login(page: Page, url: str) -> None:
    """
    Buka URL target dan tunggu user login manual.
    Script berlanjut setelah user menekan ENTER di terminal.
    """
    logger.info("Membuka halaman target: %s", url)
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)
    except PlaywrightTimeoutError:
        logger.warning("Timeout saat memuat halaman awal — lanjut menunggu login.")
    except PlaywrightError as exc:
        logger.warning("Gagal navigasi awal (%s) — lanjut menunggu login.", exc)

    print("\n" + "=" * 70)
    print("  LOGIN MANUAL")
    print("  1. Jika belum login, silakan login di jendela browser.")
    print("  2. Pastikan daftar kursus 'My Learning' sudah terlihat.")
    print("  3. Setelah siap, kembali ke terminal dan tekan ENTER.")
    print("=" * 70 + "\n")

    try:
        input(">> Tekan ENTER untuk mulai scraping... ")
    except (EOFError, KeyboardInterrupt):
        logger.error("Input dibatalkan oleh user. Keluar.")
        sys.exit(1)

    logger.info("Melanjutkan proses scraping.")


# --------------------------------------------------------------------------- #
# Helper: ambil teks aman dari elemen
# --------------------------------------------------------------------------- #
def _safe_inner_text(handle, selectors: List[str]) -> Optional[str]:
    """
    Coba beberapa selector, kembalikan inner_text pertama yang ditemukan.
    Mengembalikan None jika semua gagal (tidak melempar error).
    """
    for sel in selectors:
        try:
            el = handle.query_selector(sel)
            if el:
                txt = (el.inner_text() or "").strip()
                if txt:
                    return txt
        except PlaywrightError:
            continue
    return None


def _extract_progress(card_text: str) -> Optional[str]:
    """
    Parsing progress dari innerText card menggunakan regex.
    Mendukung format: '45% complete', '45 % selesai', '12/30', dll.
    """
    if not card_text:
        return None

    # Pola persentase: "45% complete" / "45 % selesai"
    pct = re.search(r"(\d{1,3})\s*%", card_text)
    if pct:
        value = int(pct.group(1))
        if 0 <= value <= 100:
            return f"{value}%"

    # Pola fraksi: "12 of 30" / "12/30"
    frac = re.search(
        r"(\d{1,3})\s*(?:/|of|dari)\s*(\d{1,3})",
        card_text,
        re.IGNORECASE,
    )
    if frac:
        return f"{frac.group(1)}/{frac.group(2)}"

    return None


def _extract_rating_status(card_text: str) -> Optional[str]:
    """
    Tentukan status rating dari innerText card.
    Mengembalikan 'rated', 'not_rated', atau None jika tak terdeteksi.
    """
    if not card_text:
        return None

    lowered = card_text.lower()

    # Indikasi sudah diberi rating (mis. "Your rating", "4.5", "rated")
    rated_patterns = [
        r"your rating",
        r"rating anda",
        r"\brated\b",
        r"sudah dinilai",
    ]
    for pat in rated_patterns:
        if re.search(pat, lowered):
            return "rated"

    # Indikasi belum diberi rating
    not_rated_patterns = [
        r"leave a rating",
        r"rate this course",
        r"beri rating",
        r"belum dinilai",
        r"your rating will help",
    ]
    for pat in not_rated_patterns:
        if re.search(pat, lowered):
            return "not_rated"

    return None


# --------------------------------------------------------------------------- #
# 3. extract_courses_from_page
# --------------------------------------------------------------------------- #
def extract_courses_from_page(
    page: Page,
    page_number: int,
    seen_urls: Set[str],
    seen_keys: Set[str],
) -> List[Dict[str, str]]:
    """
    Ekstrak semua course card yang tampil pada halaman saat ini.

    Strategi selector fleksibel:
        - cari semua anchor dengan href mengandung '/course/'
        - naik ke card container (parent) dari anchor tersebut
        - parsing innerText untuk progress & rating dengan regex
        - fallback jika sebuah field tidak ditemukan
    """
    results: List[Dict[str, str]] = []

    try:
        anchors = page.query_selector_all('a[href*="/course/"]')
    except PlaywrightError as exc:
        logger.error("Gagal mengambil anchor course: %s", exc)
        return results

    logger.info("Halaman %d: ditemukan %d anchor '/course/'.", page_number, len(anchors))

    for anchor in anchors:
        try:
            href = anchor.get_attribute("href") or ""
        except PlaywrightError:
            href = ""

        if "/course/" not in href:
            continue

        # Normalisasi URL menjadi absolut
        course_url = href.strip()
        if course_url.startswith("/"):
            course_url = "https://www.udemy.com" + course_url
        # Buang query string agar dedup lebih konsisten
        course_url = course_url.split("?")[0].rstrip("/")

        # --- Cari card container (parent) dari anchor ---
        card = None
        try:
            card = anchor.evaluate_handle(
                """
                (el) => {
                    let node = el;
                    for (let i = 0; i < 6 && node; i++) {
                        const cls = (node.className || "").toString().toLowerCase();
                        if (cls.includes("card") || cls.includes("course") ||
                            node.getAttribute("data-purpose")) {
                            return node;
                        }
                        node = node.parentElement;
                    }
                    return el.parentElement || el;
                }
                """
            ).as_element()
        except PlaywrightError:
            card = None

        if card is None:
            card = anchor  # fallback: pakai anchor itu sendiri

        # --- innerText card (untuk regex progress & rating) ---
        try:
            card_text = (card.inner_text() or "").strip()
        except PlaywrightError:
            card_text = ""

        # --- Course title (fallback berlapis) ---
        title = _safe_inner_text(
            card,
            [
                '[data-purpose="course-title-url"]',
                "h3",
                "h2",
                '[class*="title"]',
            ],
        )
        if not title:
            try:
                title = (anchor.inner_text() or "").strip() or None
            except PlaywrightError:
                title = None
        if not title:
            title = "N/A"
        title = re.sub(r"\s+", " ", title).strip()

        # --- Instructor (fallback berlapis) ---
        instructor = _safe_inner_text(
            card,
            [
                '[data-purpose="instructor-name"]',
                '[class*="instructor"]',
                '[class*="visitor"]',
            ],
        )
        if not instructor:
            instructor = "N/A"
        instructor = re.sub(r"\s+", " ", instructor).strip()

        # --- Progress (regex dari innerText) ---
        progress = _extract_progress(card_text) or "N/A"

        # --- Rating status ---
        rating_status = _extract_rating_status(card_text) or "unknown"

        # --- Deduplikasi ---
        dedup_key = f"{title}||{progress}"
        if course_url and course_url in seen_urls:
            continue
        if dedup_key in seen_keys:
            continue

        if course_url:
            seen_urls.add(course_url)
        seen_keys.add(dedup_key)

        record = {
            "page": str(page_number),
            "course_title": title,
            "instructor": instructor,
            "progress": progress,
            "rating_status": rating_status,
            "course_url": course_url or "N/A",
        }
        results.append(record)

    logger.info("Halaman %d: %d kursus unik diambil.", page_number, len(results))
    return results


# --------------------------------------------------------------------------- #
# 4. scroll_and_collect_courses
# --------------------------------------------------------------------------- #
def scroll_and_collect_courses(
    page: Page,
    page_number: int,
    seen_urls: Set[str],
    seen_keys: Set[str],
    max_scrolls: int = 30,
    pause: float = 1.2,
) -> List[Dict[str, str]]:
    """
    Auto-scroll halaman agar semua course card termuat (lazy-load),
    lalu ekstrak datanya.
    """
    logger.info("Halaman %d: memulai auto-scroll...", page_number)

    last_height = 0
    stable_rounds = 0

    for i in range(max_scrolls):
        try:
            page.mouse.wheel(0, 4000)
        except PlaywrightError:
            try:
                page.evaluate("window.scrollBy(0, 4000);")
            except PlaywrightError:
                break

        time.sleep(pause)

        try:
            new_height = page.evaluate("document.body.scrollHeight")
        except PlaywrightError:
            new_height = last_height

        if new_height == last_height:
            stable_rounds += 1
            if stable_rounds >= 2:
                logger.info(
                    "Halaman %d: tinggi stabil, scroll selesai (iterasi %d).",
                    page_number,
                    i + 1,
                )
                break
        else:
            stable_rounds = 0

        last_height = new_height

    # Scroll kembali ke atas agar render konsisten
    try:
        page.evaluate("window.scrollTo(0, 0);")
        time.sleep(0.5)
    except PlaywrightError:
        pass

    return extract_courses_from_page(page, page_number, seen_urls, seen_keys)


# --------------------------------------------------------------------------- #
# 5. go_to_next_page
# --------------------------------------------------------------------------- #
def go_to_next_page(page: Page) -> bool:
    """
    Pindah ke halaman berikutnya bila tombol Next tersedia & aktif.

    Mengembalikan:
        True  -> berhasil pindah halaman.
        False -> tidak ada Next / Next disabled.
    """
    next_selectors = [
        'a[data-page="next"]',
        'button[aria-label*="Next"]',
        'a[aria-label*="Next"]',
        'button[aria-label*="Berikutnya"]',
        '[data-purpose="next-page"]',
        'a[rel="next"]',
    ]

    next_btn = None
    for sel in next_selectors:
        try:
            candidate = page.query_selector(sel)
            if candidate:
                next_btn = candidate
                break
        except PlaywrightError:
            continue

    if next_btn is None:
        logger.info("Tombol Next tidak ditemukan — pagination selesai.")
        return False

    # Cek apakah tombol disabled
    try:
        is_disabled = next_btn.get_attribute("disabled") is not None
        aria_disabled = (next_btn.get_attribute("aria-disabled") or "").lower() == "true"
        is_visible = next_btn.is_visible()
        is_enabled = next_btn.is_enabled()
    except PlaywrightError:
        is_disabled = aria_disabled = False
        is_visible = is_enabled = True

    if is_disabled or aria_disabled or not is_visible or not is_enabled:
        logger.info("Tombol Next disabled/tidak aktif — pagination selesai.")
        return False

    try:
        next_btn.scroll_into_view_if_needed(timeout=5_000)
        next_btn.click(timeout=10_000)
        logger.info("Mengklik Next, menunggu halaman berikutnya termuat...")
        page.wait_for_load_state("networkidle", timeout=20_000)
        time.sleep(1.5)
        return True
    except PlaywrightTimeoutError:
        logger.warning("Timeout saat pindah halaman — menghentikan pagination.")
        return False
    except PlaywrightError as exc:
        logger.warning("Gagal mengklik Next (%s) — menghentikan pagination.", exc)
        return False


# --------------------------------------------------------------------------- #
# 6. save_to_csv
# --------------------------------------------------------------------------- #
def save_to_csv(courses: List[Dict[str, str]], output_path: str) -> None:
    """
    Simpan hasil ke CSV dengan encoding utf-8-sig (aman dibuka di Excel).
    Kolom: no,page,course_title,instructor,progress,rating_status,course_url
    """
    fieldnames = [
        "no",
        "page",
        "course_title",
        "instructor",
        "progress",
        "rating_status",
        "course_url",
    ]

    try:
        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for idx, course in enumerate(courses, start=1):
                row = {"no": idx}
                row.update({k: course.get(k, "N/A") for k in fieldnames if k != "no"})
                writer.writerow(row)
        logger.info("Berhasil menyimpan %d kursus ke '%s'.", len(courses), output_path)
    except OSError as exc:
        logger.error("Gagal menulis CSV '%s': %s", output_path, exc)


# --------------------------------------------------------------------------- #
# 7. main
# --------------------------------------------------------------------------- #
def main() -> None:
    args = parse_args()

    target_url = resolve_target_url(args)

    all_courses: List[Dict[str, str]] = []
    seen_urls: Set[str] = set()
    seen_keys: Set[str] = set()

    logger.info("Memulai Udemy scraper.")
    logger.info("Output  : %s", args.output)
    logger.info("Target  : %s", target_url)
    logger.info("Max page: %s", args.max_pages if args.max_pages else "tidak dibatasi")
    logger.info("Headless: %s", args.headless)

    with sync_playwright() as p:
        try:
            try:
                browser = p.chromium.launch(headless=args.headless)
            except PlaywrightError as exc:
                logger.error("Gagal meluncurkan Chromium: %s", exc)
                sys.exit(1)

            context = browser.new_context(
                viewport={"width": 1440, "height": 900},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
            )
            page = context.new_page()

            try:
                # Login manual + tunggu ENTER
                wait_for_manual_login(page, target_url)

                page_number = 1
                while True:
                    logger.info("=" * 50)
                    logger.info("Memproses halaman %d", page_number)
                    logger.info("=" * 50)

                    try:
                        page_courses = scroll_and_collect_courses(
                            page, page_number, seen_urls, seen_keys
                        )
                        all_courses.extend(page_courses)
                    except PlaywrightError as exc:
                        logger.error("Error saat scraping halaman %d: %s", page_number, exc)

                    # Cek batas max-pages
                    if args.max_pages is not None and page_number >= args.max_pages:
                        logger.info(
                            "Mencapai batas --max-pages (%d). Berhenti.",
                            args.max_pages,
                        )
                        break

                    # Pindah halaman berikutnya
                    if not go_to_next_page(page):
                        break

                    page_number += 1

            except KeyboardInterrupt:
                logger.warning("Dihentikan oleh user (Ctrl+C). Menyimpan data sementara...")
            except Exception as exc:  # safety net agar tidak crash mentah
                logger.error("Error tak terduga: %s", exc)
            finally:
                logger.info("Total kursus terkumpul: %d", len(all_courses))
                if all_courses:
                    save_to_csv(all_courses, args.output)
                else:
                    logger.warning("Tidak ada kursus terkumpul — CSV tidak ditulis.")

                try:
                    context.close()
                    browser.close()
                except PlaywrightError:
                    pass

        except Exception as exc:
            # safety net level luar
            logger.error("Fatal error: %s", exc)
            raise

    logger.info("Selesai. 🎉")


if __name__ == "__main__":
    main()
