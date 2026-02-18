import os

from docx import Document
import PyPDF2

from app.prompts import build_prompt, instruksi_gaya


class AnalysisService:
    def __init__(self, ai_client):
        self.ai_client = ai_client
        self.ai_ready = False

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
        """Membaca teks dari file PDF atau DOCX."""
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
            else:
                print("⚠️ Format modul tidak didukung (Gunakan PDF/DOCX).")
            return text
        except Exception as e:
            print(f"⚠️ Gagal membaca modul: {e}")
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

    @staticmethod
    def _instruksi_kualitas_langkah():
        return (
            "\n"
            "                ATURAN KUALITAS & KUANTITAS:\n"
            "                1. WAJIB HASILKAN ANTARA MINIMAL 7 SAMPAI MAKSIMAL 12 BARIS LANGKAH.\n"
            "                2. Jika langkah asli terlalu sedikit (<7): Pecah langkah kompleks menjadi lebih detail.\n"
            "                3. Jika langkah asli terlalu banyak (>12): Gabungkan langkah-langkah kecil/remeh menjadi satu baris.\n"
            "                4. ISI HARUS PADAT & TEKNIS: Hindari kalimat \"Buka aplikasi\" saja. Gunakan \"Buka IntelliJ IDEA dan tunggu loading selesai\".\n"
            "                5. DILARANG memasukkan langkah sampah seperti \"Siapkan PC\", \"Berdoa\", atau \"Selesai\". Langsung ke teknis.\n"
            "                6. JANGAN PAKAI NOMOR (1. 2. 3.) dan Bullet Points (*, -, •). Python yang akan memberi nomor nanti.\n"
            "                "
        )

    def generate_langkah_kerja(self, judul_sub, modul_text, image_path=None):
        if not self.ensure_ready():
            return None, "AI tidak bisa connect. Periksa API key."

        instruksi = self._instruksi_kualitas_langkah()
        if modul_text:
            prompt = (
                "\n                    Peran: Asisten Lab Komputer.\n"
                f"                    Tugas: Ekstrak Langkah Kerja Praktikum untuk sub-bab \"{judul_sub}\".\n\n"
                "                    Konteks Modul:\n"
                f"                    {modul_text}\n\n"
                "                    Instruksi Ekstraksi:\n"
                f"                    1. Cari area teks yang membahas \"{judul_sub}\".\n"
                "                    2. Ambil intisari langkah-langkahnya.\n\n"
                f"                    {instruksi}\n"
                "                    "
            )
            raw = self.ai_client.ask(prompt)
        else:
            prompt = (
                "\n                        Peran: Asisten Lab Komputer.\n"
                "                        Tugas: Buat simulasi Langkah Kerja berdasarkan Screenshot ini.\n\n"
                "                        Instruksi Analisa:\n"
                "                        1. Lihat UI/Codingan di gambar.\n"
                "                        2. Rekonstruksi urutan langkah logis (step-by-step) yang dilakukan user untuk mencapai hasil di gambar tersebut.\n\n"
                f"                        {instruksi}\n"
                "                        "
            )
            raw = self.ai_client.ask(prompt, image_path)

        if not raw or "Gagal" in raw:
            return None, "AI tidak bisa menjawab."

        return self.format_langkah_kerja(raw), None

    def generate_analysis(self, tipe, isi_a_text, kode_items, gambar_items, template_choice):
        if not self.ensure_ready():
            return None, "AI tidak bisa connect. Periksa API key."

        isi_a = isi_a_text
        if tipe == "1":
            isi_a = self.concat_kode_for_prompt(kode_items)

        prompt = build_prompt(tipe, isi_a, instruksi_gaya())
        image_path = gambar_items[0]["path"] if gambar_items else None
        result = self.ai_client.ask(prompt, image_path)

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
        )

        result = self.ai_client.ask(prompt)
        if not result or "Gagal" in result:
            return None, "AI tidak bisa menjawab."
        return result, None

    def generate_conclusion(self, bab1_items, bab2_items):
        if not self.ensure_ready():
            return None, "AI tidak bisa connect. Periksa API key."

        bab1_text = self._format_bab_items(bab1_items, "BAB 1")
        bab2_text = self._format_bab_items(bab2_items, "BAB 2")

        prompt = (
            "Peran: Asisten penyusun laporan praktikum.\n"
            "Tugas: Buat kesimpulan laporan berdasarkan ringkasan berikut.\n\n"
            f"{bab1_text}\n\n"
            f"{bab2_text}\n\n"
            "Instruksi:\n"
            "1. Tulis tepat 3 paragraf.\n"
            "2. Tiap paragraf 5-10 kalimat.\n"
            "3. Gunakan Bahasa Indonesia formal dan akademis.\n"
            "4. Fokus pada tujuan, hasil, kendala, dan pembelajaran.\n"
            "5. Jangan gunakan tanda kutip atau backtick.\n"
        )

        result = self.ai_client.ask(prompt)
        if not result or "Gagal" in result:
            return None, "AI tidak bisa menjawab."
        return result, None
