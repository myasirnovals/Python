"""Porting lengkap dari generator_laporan.py - CLI generator laporan."""

import os

from docxtpl import DocxTemplate, RichText

from .ai_client import GeminiClient
from .doc_helpers import ImageDocumentHelper
from .input_helpers import ConsoleInput
from .prompts import PromptBuilder
from .sections import ReportSectionsCollector
from .services.analysis_service import AnalysisService
from .services.report_service import ReportService


class LegacyCliGenerator:
    """OOP wrapper for legacy interactive CLI report generation flow."""

    def __init__(
        self,
        templates_dir="templates",
        input_reader=None,
        image_helper=None,
        gemini_client=None,
        prompt_builder=None,
        analysis_service=None,
        report_service=None,
    ):
        self.templates_dir = templates_dir
        self.input_reader = input_reader or ConsoleInput()
        self.image_helper = image_helper or ImageDocumentHelper()
        self.gemini_client = gemini_client or GeminiClient()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.analysis_service = analysis_service or AnalysisService(self.gemini_client)
        self.report_service = report_service or ReportService(templates_dir=templates_dir)
        self.sections_collector = ReportSectionsCollector(
            templates_dir=self.templates_dir,
            input_reader=self.input_reader,
            prompt_builder=self.prompt_builder,
            image_helper=self.image_helper,
        )

    def _select_template(self):
        return self.sections_collector.pilih_template()

    @staticmethod
    def _print_banner():
        print("\n==============================================")
        print("   GENERATOR LAPORAN HYBRID (Structure + AI)  ")
        print("==============================================")

    def _input_cover_data(self):
        return self.sections_collector.input_cover()

    def _input_modul_text(self):
        print("\n   [OPSIONAL] File Modul Praktikum (PDF/Word)")
        path_modul = input("   Path File Modul (Kosongkan jika tidak ada): ")

        if not path_modul.strip():
            return ""

        print("   📖 Sedang membaca isi modul...")
        isi_teks_modul = self.analysis_service.read_modul_text(path_modul)
        if isi_teks_modul:
            print(f"   ✅ Modul berhasil dimuat! ({len(isi_teks_modul)} karakter)")
        else:
            print("   ⚠️ Modul kosong atau gagal dibaca.")
        return isi_teks_modul

    @staticmethod
    def _prompt_langkah_quality_rules():
        return """
                    ATURAN KUALITAS & KUANTITAS:
                    1. WAJIB HASILKAN ANTARA MINIMAL 7 SAMPAI MAKSIMAL 12 BARIS LANGKAH.
                    2. Jika langkah asli terlalu sedikit (<7): Pecah langkah kompleks menjadi lebih detail.
                    3. Jika langkah asli terlalu banyak (>12): Gabungkan langkah-langkah kecil/remeh menjadi satu baris.
                    4. ISI HARUS PADAT & TEKNIS: Hindari kalimat "Buka aplikasi" saja. Gunakan "Buka IntelliJ IDEA dan tunggu loading selesai".
                    5. DILARANG memasukkan langkah sampah seperti "Siapkan PC", "Berdoa", atau "Selesai". Langsung ke teknis.
                    6. JANGAN PAKAI NOMOR (1. 2. 3.) dan Bullet Points (*, -, •). Python yang akan memberi nomor nanti.
                    """

    def _collect_source_code(self):
        data_kode_mentah = []
        counter_kode = 1

        print("   [Input Source Code]")
        while True:
            print(f"\n     --- File Kode ke-{counter_kode} ---")
            nama_file = input("     Nama File (misal: Main.java): ")
            print(f"     Paste isi kode '{nama_file}' di bawah:")
            isi_mentah = self.input_reader.input_multiline("     Isi Kode")

            data_kode_mentah.append({"nama": nama_file, "isi": isi_mentah})
            counter_kode += 1
            if input("     Tambah file kode lagi? (y/n): ").lower() != "y":
                break

        list_kode_final = []
        if data_kode_mentah:
            for i, d in enumerate(data_kode_mentah, 1):
                if len(data_kode_mentah) > 1:
                    prefix = "\n" if i > 1 else ""
                    teks_judul = f"{prefix}{i}. {d['nama']}"
                    judul_tampil = RichText(teks_judul)
                else:
                    judul_tampil = "##HAPUS##"

                list_kode_final.append({"judul": judul_tampil, "isi": d["isi"]})

        temp_list_ai = []
        for d in data_kode_mentah:
            temp_list_ai.append(f"File: {d['nama']}\n{d['isi']}")
        isi_a = "\n\n".join(temp_list_ai)
        return isi_a, list_kode_final

    def _generate_langkah_kerja_ai(self, judul_sub, isi_teks_modul):
        instruksi_kualitas = self._prompt_langkah_quality_rules()

        if isi_teks_modul:
            prompt_langkah = f"""
                        Peran: Asisten Lab Komputer.
                        Tugas: Ekstrak Langkah Kerja Praktikum untuk sub-bab "{judul_sub}".

                        Konteks Modul:
                        {isi_teks_modul}

                        Instruksi Ekstraksi:
                        1. Cari area teks yang membahas "{judul_sub}".
                        2. Ambil intisari langkah-langkahnya.

                        {instruksi_kualitas}
                        """
            return self.gemini_client.ask(prompt_langkah)

        print("      ⚠️ Tidak ada file modul. AI akan melihat dari screenshot.")
        path_sementara = input("      Masukkan path gambar untuk dianalisa: ").replace('"', "")
        if path_sementara and os.path.exists(path_sementara):
            prompt_langkah = f"""
                            Peran: Asisten Lab Komputer.
                            Tugas: Buat simulasi Langkah Kerja berdasarkan Screenshot ini.

                            Instruksi Analisa:
                            1. Lihat UI/Codingan di gambar.
                            2. Rekonstruksi urutan langkah logis (step-by-step) yang dilakukan user untuk mencapai hasil di gambar tersebut.

                            {instruksi_kualitas}
                            """
            return self.gemini_client.ask(prompt_langkah, path_sementara)

        print("      ❌ Gambar tidak ditemukan. Beralih ke manual.")
        return ""

    def _collect_langkah_kerja(self, judul_sub, isi_teks_modul):
        print("\n   [Input Langkah Kerja]")
        raw_isi = ""
        pakai_ai = input("   🤖 Gunakan AI untuk buat langkah kerja? (y/n): ").lower()

        if pakai_ai == "y":
            print("      ⏳ Sedang berpikir...")
            raw_isi = self._generate_langkah_kerja_ai(judul_sub, isi_teks_modul)
            if raw_isi and "Gagal" not in raw_isi:
                print("      ✅ Langkah Kerja dari AI siap! (Format akan otomatis dirapikan)")
            else:
                print("      ⚠️ AI tidak bisa menjawab. Silakan ketik manual.")
                raw_isi = self.input_reader.input_multiline("   Masukkan Langkah Kerja")
        else:
            print("   (Ketik langkah per baris, Python akan memberi nomor otomatis)")
            raw_isi = self.input_reader.input_multiline("   Masukkan Langkah Kerja")

        if not raw_isi:
            raw_isi = "Langkah kerja tidak diisi."

        lines = raw_isi.split("\n")
        list_bernomor = []
        nomor_urut = 1
        for baris in lines:
            teks = baris.strip()
            teks_bersih = teks.lstrip(" *-•.1234567890").strip()
            if teks_bersih:
                if nomor_urut == 1:
                    item_baru = f"\u200B{nomor_urut}. {teks_bersih}"
                else:
                    item_baru = f" {nomor_urut}. {teks_bersih}"
                list_bernomor.append(item_baru)
                nomor_urut += 1

        return "\n".join(list_bernomor) + "\n"

    def _collect_bab1_gambar(self, doc, counter_gbr_bab1):
        list_gbr = []
        path_gambar_utama = ""

        print("   [Input Gambar Hasil]")
        while True:
            path = input(f"     File Gambar (utk Gambar 1.{counter_gbr_bab1}): ")
            if not path:
                break

            if not path_gambar_utama:
                path_gambar_utama = path

            obj = self.image_helper.muat_gambar(doc, path)
            if obj:
                cap = input("     Caption: ")
                caption_fix = cap + "\n"
                list_gbr.append(
                    {
                        "objek_gambar": obj,
                        "caption": caption_fix,
                        "nomor_tampil": counter_gbr_bab1,
                    }
                )
                counter_gbr_bab1 += 1

            if input("     Tambah gambar lagi? (y/n): ").lower() != "y":
                break

        return list_gbr, path_gambar_utama, counter_gbr_bab1

    def _collect_analisa(self, pilih_tipe, isi_a, path_gambar_utama, pilihan_tpl):
        analisa = ""
        print("\n   [Input Analisa]")
        if input("   🤖 Gunakan AI untuk analisa? (y/n): ").lower() == "y":
            instruksi_gaya = self.prompt_builder.instruksi_gaya()
            prompt = self.prompt_builder.build_prompt(pilih_tipe, isi_a, instruksi_gaya)
            analisa = self.gemini_client.ask(prompt, path_gambar_utama)
            if pilihan_tpl == "1" and analisa:
                analisa = analisa.replace("\n\n", "\n")
                analisa = "\t" + analisa.replace("\n", "\n\t")
            print(f"   ✅ Hasil AI: Selesai ({len(analisa)} karakter)")
        else:
            analisa = self.input_reader.input_multiline("   Masukkan Analisa Manual")
            if pilihan_tpl == "1" and analisa:
                analisa = analisa.replace("\n\n", "\n")
                analisa = "\t" + analisa.replace("\n", "\n\t")

        return analisa

    def _collect_bab1(self, doc, pilihan_tpl, isi_teks_modul):
        print("\n--- [BAGIAN 2] BAB 1 HASIL PRAKTIKUM ---")
        daftar_sub_bab1 = []
        nomor_sub = 1
        counter_gbr_bab1 = 1

        while True:
            print(f"\n   >>> Sub-Bab 1.{nomor_sub}")
            judul_sub = input("   Judul Sub-Bab: ")

            print("   Tipe Point A: [1] Source Code  [2] Langkah Kerja")
            pilih_tipe = input("   Pilih (1/2): ")

            list_kode_final = []
            if pilih_tipe == "2":
                label_a = "Langkah Kerja"
                isi_a = self._collect_langkah_kerja(judul_sub, isi_teks_modul)
            else:
                label_a = "Source Code"
                isi_a, list_kode_final = self._collect_source_code()

            list_gbr, path_gambar_utama, counter_gbr_bab1 = self._collect_bab1_gambar(
                doc, counter_gbr_bab1
            )
            analisa = self._collect_analisa(pilih_tipe, isi_a, path_gambar_utama, pilihan_tpl)

            daftar_sub_bab1.append(
                {
                    "judul_sub_bab": judul_sub,
                    "label_point_a": label_a,
                    "isi_point_a": isi_a,
                    "list_gambar": list_gbr,
                    "isi_analisa": analisa,
                    "list_kode": list_kode_final,
                }
            )

            if input(f"\n   Lanjut ke Sub-Bab 1.{nomor_sub + 1}? (y/n): ").lower() != "y":
                break
            nomor_sub += 1

        return daftar_sub_bab1

    def _collect_bab2(self, doc):
        daftar_tugas = self.sections_collector.input_bab2(doc)
        return self._normalize_task_captions(daftar_tugas)

    def _collect_kesimpulan(self):
        return self.sections_collector.input_bab3()

    @staticmethod
    def _normalize_task_captions(daftar_tugas):
        for tugas in daftar_tugas:
            for gambar in tugas.get("list_gambar", []):
                caption = gambar.get("caption", "")
                if caption and not caption.endswith("\n"):
                    gambar["caption"] = caption + "\n"
        return daftar_tugas

    def _build_context(self, cover_data, daftar_sub_bab1, daftar_tugas, isi_kesimpulan):
        context = dict(cover_data)
        context.update(
            {
                "daftar_sub_bab": daftar_sub_bab1,
                "daftar_tugas": daftar_tugas,
                "isi_kesimpulan": isi_kesimpulan,
            }
        )
        return context

    def _save_report_document(self, doc, context, nomor_modul, nama):
        print("\n--- MENYIMPAN FILE... ---")
        try:
            nama_file = f"Laporan_Modul_{nomor_modul}_{nama.replace(' ', '_')}.docx"
            doc.render(context, autoescape=True)
            doc.save(nama_file)
            print(f"✅ BERHASIL! File tersimpan: {nama_file}")

            self.report_service.postprocess_document(nama_file)

            print(f"🎉 SELESAI! File {nama_file} sudah rapi & rapat.")
        except Exception as e:
            print(f"❌ Gagal render: {e}")

    def run(self):
        pilihan_tpl, nama_template = self._select_template()

        if not os.path.exists(nama_template):
            print(f"❌ Error: File '{nama_template}' tidak ditemukan!")
            print("   Pastikan Anda sudah membuat 2 file template sesuai panduan.")
            return

        model_name = self.gemini_client.get_active_model()
        if not model_name:
            print("⛔ Program berhenti karena AI tidak bisa connect.")
            return

        doc = DocxTemplate(nama_template)
        self._print_banner()
        cover_data = self._input_cover_data()
        isi_teks_modul = self._input_modul_text()
        daftar_sub_bab1 = self._collect_bab1(doc, pilihan_tpl, isi_teks_modul)
        daftar_tugas = self._collect_bab2(doc)
        isi_kesimpulan = self._collect_kesimpulan()
        context = self._build_context(
            cover_data,
            daftar_sub_bab1,
            daftar_tugas,
            isi_kesimpulan,
        )
        self._save_report_document(
            doc,
            context,
            cover_data["nomor_modul"],
            cover_data["nama"],
        )

    def render_report(self, template, context: dict, output_path: str, pilihan_tpl: str = "1"):
        """Render report given template path/template object and context."""
        try:
            if isinstance(template, str):
                doc = DocxTemplate(template)
            else:
                doc = template

            doc.render(context, autoescape=True)
            doc.save(output_path)

            try:
                self.report_service.postprocess_document(output_path)
            except Exception:
                pass

            return True, None
        except Exception as e:
            return False, str(e)


def main():
    LegacyCliGenerator().run()


if __name__ == "__main__":
    main()


def render_report(template, context: dict, output_path: str, pilihan_tpl: str = "1"):
    """Backward-compatible module entrypoint for render flow."""
    return LegacyCliGenerator().render_report(template, context, output_path, pilihan_tpl)
