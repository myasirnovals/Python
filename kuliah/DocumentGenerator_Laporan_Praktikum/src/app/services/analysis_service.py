import os
import re
import time
import PyPDF2

from docx import Document
from app.prompts import PromptBuilder

try:
    import win32com.client as win32
except Exception:  # pragma: no cover - optional dependency
    win32 = None


class AnalysisService:
    def __init__(self, ai_client):
        self.ai_client = ai_client
        self.ai_ready = False
        self.prompt_builder = PromptBuilder()

    def ensure_ready(self):
        if self.ai_ready:
            return True
        if not self.ai_client.get_active_model():
            return False
        self.ai_ready = True
        return True

    @staticmethod
    def concat_kode_for_prompt(kode_items):
        parts = []
        for item in kode_items:
            name = item.get("nama_file") or item.get("nama") or item.get("judul_kode") or item.get("judul") or ""
            content = item.get("isi_kode") or item.get("isi") or ""
            header = f"File: {name}" if name else "File"
            parts.append(f"{header}\n{content}")
        return "\n\n".join(parts)

    @staticmethod
    def read_modul_text(path_file):
        """Membaca teks dari file PDF, DOCX, atau DOC."""
        if not path_file or not os.path.exists(path_file):
            return ""

        ext = path_file.lower().split(".")[-1]
        text = ""
        try:
            if ext == "pdf":
                with open(path_file, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text += (page.extract_text() or "") + "\n"
            elif ext == "docx":
                doc = Document(path_file)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            elif ext == "doc":
                if win32 is None:
                    print("[INFO] pywin32 tidak tersedia untuk membaca file DOC.")
                    return ""
                word_app = None
                doc_obj = None
                try:
                    word_app = win32.Dispatch("Word.Application")
                    word_app.Visible = False
                    word_app.DisplayAlerts = False
                    doc_obj = word_app.Documents.Open(os.path.abspath(path_file))
                    text = doc_obj.Content.Text or ""
                finally:
                    if doc_obj is not None:
                        doc_obj.Close(False)
                    if word_app is not None:
                        word_app.Quit()
            else:
                print("[INFO] Format modul tidak didukung (Gunakan PDF/DOC/DOCX).")
            return text
        except Exception as e:
            print(f"[ERROR] Gagal membaca modul: {e}")
            return ""

    @staticmethod
    def format_langkah_kerja(raw_text):
        if not raw_text:
            return "Langkah kerja tidak diisi."

        lines = raw_text.split("\n")
        list_bernomor = []
        nomor_urut = 1
        for baris in lines:
            teks = baris.strip()
            teks_bersih = teks.lstrip(" *-•.1234567890").strip()
            if not teks_bersih:
                continue

            if nomor_urut == 1:
                item_baru = f"\u200B{nomor_urut}. {teks_bersih}"
            else:
                item_baru = f" {nomor_urut}. {teks_bersih}"
            list_bernomor.append(item_baru)
            nomor_urut += 1

        return "\n".join(list_bernomor) + "\n"

    @staticmethod
    def _safe_text(text, max_len=800):
        if not text:
            return ""
        cleaned = str(text).strip()
        if len(cleaned) <= max_len:
            return cleaned
        return cleaned[:max_len].rstrip() + "..."

    @staticmethod
    def _clean_single_paragraph(text):
        if not text:
            return ""
        return " ".join(str(text).replace("\n", " ").split()).strip()

    @staticmethod
    def _split_sentences(text):
        cleaned = AnalysisService._clean_single_paragraph(text)
        if not cleaned:
            return []

        parts = re.split(r"(?<=[.!?])\s+", cleaned)
        sentences = []
        for part in parts:
            sentence = part.strip()
            if not sentence:
                continue
            if sentence[-1] not in ".!?":
                sentence += "."
            sentences.append(sentence)
        return sentences

    @staticmethod
    def _limit_sentences(text, min_sentences=3, max_sentences=5):
        """Membatasi jumlah kalimat antara 3 sampai 5 tanpa melakukan duplikasi buatan."""
        sentences = AnalysisService._split_sentences(text)
        if not sentences:
            return ""
        if len(sentences) > max_sentences:
            return " ".join(sentences[:max_sentences])
        return " ".join(sentences)

    @staticmethod
    def _extract_relevant_modul_excerpt(modul_text, query, max_len=6000):
        """Mengekstrak potongan modul yang relevan dengan topik atau sub-bab."""
        if not modul_text:
            return ""
        text = str(modul_text).strip()
        if len(text) <= max_len:
            return text

        keywords = [
            k for k in re.split(r"\W+", str(query).lower())
            if len(k) > 2 and k not in {"sub", "bab", "tugas", "dan", "yang", "pada", "untuk", "dari"}
        ]
        best_pos = -1
        for kw in keywords:
            pos = text.lower().find(kw)
            if pos != -1:
                best_pos = pos
                break

        if best_pos != -1:
            start = max(0, best_pos - 500)
            end = min(len(text), start + max_len)
            return text[start:end]

        return text[:max_len]

    @staticmethod
    def _format_kode_names(kode_items):
        names = []
        for item in kode_items or []:
            name = (
                item.get("nama_file")
                or item.get("nama")
                or item.get("judul_kode")
                or item.get("judul")
                or ""
            ).strip()
            if name:
                names.append(name)
        return ", ".join(names)

    def _format_bab_items(self, bab_items, label):
        lines = [f"{label}: {len(bab_items)} item"]
        for idx, item in enumerate(bab_items, 1):
            judul = (item.get("judul_tugas") or item.get("judul_sub_bab") or "").strip()
            tipe = (item.get("tipe_konten") or item.get("tipe") or "").strip()
            header = f"{idx}. {judul}" if judul else f"{idx}. (tanpa judul)"
            if tipe:
                header += f" (tipe {tipe})"
            lines.append(header)

            penjelasan = self._safe_text(
                item.get("penjelasan_singkat") or item.get("deskripsi_singkat", ""),
                400,
            )
            if penjelasan:
                lines.append(f"- penjelasan: {penjelasan}")

            if tipe == "1":
                kode_names = self._format_kode_names(
                    item.get("kode_items") or item.get("kode_files", [])
                )
                if kode_names:
                    lines.append(f"- kode: {kode_names}")
            if tipe == "2":
                isi = self._safe_text(item.get("isi_deskripsi") or item.get("isi_a", ""))
                if isi:
                    lines.append(f"- isi: {isi}")
            if tipe == "3":
                qa_list = item.get("qa_items") or item.get("qa_list", [])
                qa_parts = []
                for q_idx, qa in enumerate(qa_list, 1):
                    q = self._safe_text(qa.get("pertanyaan") or qa.get("q", ""), 200)
                    a = self._safe_text(qa.get("jawaban") or qa.get("a", ""), 200)
                    if q or a:
                        qa_parts.append(f"{q_idx}) Q: {q} | A: {a}")
                if qa_parts:
                    lines.append("- qa: " + " ; ".join(qa_parts))

            analisa = self._safe_text(
                item.get("isi_analisa_tugas") or item.get("analisa", ""),
                400,
            )
            if analisa:
                lines.append(f"- analisa: {analisa}")

        return "\n".join(lines)

    def generate_langkah_kerja(
        self,
        judul_sub,
        modul_text="",
        image_path=None,
        cover_data=None,
        modul_path="",
        isi_deskripsi="",
    ):
        """Generate langkah kerja teknis bergaya catatan praktikum manusia (7-12 baris)."""
        if not self.ensure_ready():
            return None, "AI tidak bisa connect. Periksa API key."

        time.sleep(1)

        judul_laporan, materi_modul = self.prompt_builder.resolve_identifiers(
            cover_data, modul_path, modul_text
        )
        modul_excerpt = self._extract_relevant_modul_excerpt(
            modul_text, judul_sub, max_len=4000
        )

        has_image = bool(image_path and os.path.exists(image_path))
        prompt = self.prompt_builder.build_langkah_kerja_prompt(
            judul_sub=judul_sub,
            judul_laporan=judul_laporan,
            materi_modul=materi_modul,
            modul_excerpt=modul_excerpt,
            has_image=has_image,
            image_context=isi_deskripsi,
        )

        valid_image = image_path if has_image else None
        raw = self.ai_client.ask(prompt, valid_image)

        if not raw or raw.startswith("Error") or raw.startswith("Gagal"):
            return None, f"AI gagal merespon: {raw}"

        return self.format_langkah_kerja(raw), None

    def generate_penjelasan_singkat(
        self,
        judul_sub,
        modul_text="",
        cover_data=None,
        modul_path="",
    ):
        """Generate draf penjelasan singkat tepat 2 paragraf, 3-5 kalimat per paragraf."""
        if not self.ensure_ready():
            return None, "AI tidak bisa connect. Periksa API key."
        if not judul_sub or not str(judul_sub).strip():
            return None, "Judul sub-bab/topik tugas belum diisi."

        judul = str(judul_sub).strip()
        judul_laporan, materi_modul = self.prompt_builder.resolve_identifiers(
            cover_data, modul_path, modul_text
        )
        modul_excerpt = self._extract_relevant_modul_excerpt(
            modul_text, judul, max_len=8000
        )

        prompt = self.prompt_builder.build_penjelasan_singkat_prompt(
            judul_sub=judul,
            judul_laporan=judul_laporan,
            materi_modul=materi_modul,
            modul_excerpt=modul_excerpt,
        )

        result = self.ai_client.ask(prompt)
        if not result or result.startswith("Error") or result.startswith("Gagal"):
            return None, "Gagal generate penjelasan singkat."

        cleaned = self.prompt_builder.sanitize_ai_output(result, is_kesimpulan=False)
        paragraphs = [p.strip() for p in cleaned.split("\n") if p.strip()]
        formatted_paras = []
        for p in paragraphs[:2]:
            sentences = self._split_sentences(p)
            if len(sentences) > 5:
                p = " ".join(sentences[:5])
            formatted_paras.append(p)

        final_text = "\n\n".join(formatted_paras)
        if not final_text:
            return None, "Gagal memformat penjelasan singkat."

        return final_text, None

    def generate_analysis(
        self,
        tipe,
        isi_a_text,
        kode_items,
        gambar_items,
        template_choice,
        judul_sub="Sub-Bab Analisa",
        modul_text="",
        cover_data=None,
        modul_path="",
    ):
        """Generate draf analisa sub-bab tepat 2 paragraf (3-5 kalimat per paragraf) bebas AI Slop."""
        if not self.ensure_ready():
            return None, "AI tidak bisa connect. Periksa API key."

        time.sleep(1)

        isi_a = isi_a_text
        if tipe == "1":
            isi_a = self.concat_kode_for_prompt(kode_items)

        judul_laporan, materi_modul = self.prompt_builder.resolve_identifiers(
            cover_data, modul_path, modul_text
        )
        modul_excerpt = self._extract_relevant_modul_excerpt(
            modul_text, judul_sub, max_len=6000
        )

        image_path = (
            gambar_items[0]["path"]
            if (gambar_items and os.path.exists(gambar_items[0].get("path", "")))
            else None
        )

        prompt = self.prompt_builder.build_analisa_prompt(
            pilih_tipe=tipe,
            isi_a=isi_a,
            judul_sub=judul_sub,
            judul_laporan=judul_laporan,
            materi_modul=materi_modul,
            modul_excerpt=modul_excerpt,
            has_image=bool(image_path),
        )

        result = self.ai_client.ask(prompt, image_path)

        if not result or result.startswith("Error") or result.startswith("Gagal"):
            return None, "Gagal generate analisa."

        result = self.prompt_builder.sanitize_ai_output(result, is_kesimpulan=False)

        paragraphs = [p.strip() for p in result.split("\n") if p.strip()]
        formatted_paras = []
        for p in paragraphs[:2]:
            sentences = self._split_sentences(p)
            if len(sentences) > 5:
                p = " ".join(sentences[:5])
            formatted_paras.append(p)
        result = "\n\n".join(formatted_paras)

        if template_choice == "1" and result:
            result = result.replace("\n\n", "\n")
            result = "\t" + result.replace("\n", "\n\t")

        return result, None

    def answer_question(self, question, modul_text):
        if not self.ensure_ready():
            return None, "AI tidak bisa connect. Periksa API key."
        if not question or not question.strip():
            return "", None
        if not modul_text or not modul_text.strip():
            return None, "Referensi modul kosong."

        prompt = (
            "Peran: Asisten lab komputer.\n"
            "Tugas: Jawab pertanyaan berdasarkan modul berikut.\n\n"
            f"MODUL:\n{modul_text}\n\n"
            f"PERTANYAAN:\n{question}\n\n"
            "Instruksi:\n"
            "1. Jawab singkat dan jelas (2-4 kalimat).\n"
            "2. Jangan membuat informasi di luar modul.\n"
            "3. Gunakan Bahasa Indonesia formal.\n"
            "4. HINDARI kata \"anda\".\n"
        )

        result = self.ai_client.ask(prompt)
        if not result or "Gagal" in result:
            return None, "AI tidak bisa menjawab."
        return self.prompt_builder.sanitize_ai_output(result), None

    def generate_conclusion(
        self,
        bab1_items,
        bab2_items,
        cover_data=None,
        modul_text="",
        modul_path="",
    ):
        """Generate draf kesimpulan tepat 3 paragraf (3-5 kalimat per paragraf) bebas AI Slop."""
        if not self.ensure_ready():
            return None, "AI tidak bisa connect. Periksa API key."

        bab1_text = self._format_bab_items(bab1_items, "BAB 1 (HASIL PRAKTIKUM)")
        bab2_text = self._format_bab_items(bab2_items, "BAB 2 (TUGAS)")

        judul_laporan, materi_modul = self.prompt_builder.resolve_identifiers(
            cover_data, modul_path, modul_text
        )
        modul_excerpt = self._safe_text(modul_text, max_len=4000)

        prompt = self.prompt_builder.build_kesimpulan_prompt(
            bab1_text=bab1_text,
            bab2_text=bab2_text,
            judul_laporan=judul_laporan,
            materi_modul=materi_modul,
            modul_excerpt=modul_excerpt,
        )

        result = self.ai_client.ask(prompt)
        if not result or result.startswith("Error") or result.startswith("Gagal"):
            return None, "AI tidak bisa menjawab."

        result = self.prompt_builder.sanitize_ai_output(result, is_kesimpulan=True)

        paragraphs = [p.strip() for p in result.split("\n") if p.strip()]
        formatted_paras = []
        for p in paragraphs[:3]:
            sentences = self._split_sentences(p)
            if len(sentences) > 5:
                p = " ".join(sentences[:5])
            formatted_paras.append(p)
        result = "\n\n".join(formatted_paras)

        return result, None
