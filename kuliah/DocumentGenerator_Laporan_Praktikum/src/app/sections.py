import os

from .doc_helpers import ImageDocumentHelper
from .input_helpers import ConsoleInput
from .prompts import PromptBuilder


class ReportSectionsCollector:
    """Collect report sections from CLI input in an OOP style."""

    def __init__(
        self,
        templates_dir,
        input_reader=None,
        prompt_builder=None,
        image_helper=None,
    ):
        self.templates_dir = templates_dir
        self.input_reader = input_reader or ConsoleInput()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.image_helper = image_helper or ImageDocumentHelper()

    def pilih_template(self):
        print("\n--- PILIH GAYA FORMAT LAPORAN ---")
        print(" [1] Gaya Rapat (Menjorok 0.7cm, Antar paragraf rapat)")
        print(" [2] Gaya Renggang (Rata Kiri, Antar paragraf ada jarak)")
        pilihan_tpl = input("Pilih (1/2): ")

        if pilihan_tpl == "2":
            nama_template = os.path.join(self.templates_dir, "format-2.docx")
            print("👉 Menggunakan: Template Renggang (Block Style)")
        else:
            nama_template = os.path.join(self.templates_dir, "format-1.docx")
            print("👉 Menggunakan: Template Rapat (Indented Style)")

        return pilihan_tpl, nama_template

    def input_cover(self):
        print("\n--- [BAGIAN 1] DATA COVER ---")
        mata_kuliah = input("Mata Kuliah : ").upper()
        nomor_modul = input("Nomor Modul : ")
        judul = input("Judul Modul : ").upper()
        nama = input("Nama        : ").upper()
        nim = input("NIM         : ")
        tahun = input("Tahun       : ")

        return {
            "mata_kuliah": mata_kuliah,
            "nomor_modul": nomor_modul,
            "judul": judul,
            "nama": nama,
            "nim": nim,
            "tahun": tahun,
        }

    def _input_source_code(self):
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
                    judul_tampil = f"{i}. {d['nama']}"
                else:
                    judul_tampil = ""

                list_kode_final.append({"judul": judul_tampil, "isi": d["isi"]})

        return list_kode_final

    def _input_bab1_content(self, pilih_tipe):
        if pilih_tipe == "2":
            return "Langkah Kerja", self.input_reader.input_multiline("   Masukkan Langkah Kerja"), []

        return "Source Code", "", self._input_source_code()

    def _input_bab1_gambar(self, doc, counter_gbr_bab1):
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
                list_gbr.append(
                    {
                        "objek_gambar": obj,
                        "caption": cap,
                        "nomor_tampil": counter_gbr_bab1,
                    }
                )
                counter_gbr_bab1 += 1

            if input("     Tambah gambar lagi? (y/n): ").lower() != "y":
                break

        return list_gbr, path_gambar_utama, counter_gbr_bab1

    def _input_bab1_analisa(self, pilih_tipe, isi_a, path_gambar_utama, pilihan_tpl, ai_client):
        print("\n   [Input Analisa]")
        if input("   🤖 Gunakan AI untuk analisa? (y/n): ").lower() == "y":
            instruksi = self.prompt_builder.instruksi_gaya()
            prompt = self.prompt_builder.build_prompt(pilih_tipe, isi_a, instruksi)

            analisa = ai_client.ask(prompt, path_gambar_utama)
            if pilihan_tpl == "1" and analisa:
                analisa = analisa.replace("\n\n", "\n")
                analisa = "\t" + analisa.replace("\n", "\n\t")

            print(f"   ✅ Hasil AI: Selesai ({len(analisa)} karakter)")
            return analisa

        return self.input_reader.input_multiline("   Masukkan Analisa Manual")

    def _input_bab1_sub_bab(self, doc, pilihan_tpl, ai_client, nomor_sub, counter_gbr_bab1):
        print(f"\n   >>> Sub-Bab 1.{nomor_sub}")
        judul_sub = input("   Judul Sub-Bab: ")

        print("   Tipe Point A: [1] Source Code  [2] Langkah Kerja")
        pilih_tipe = input("   Pilih (1/2): ")

        label_a, isi_a, list_kode_final = self._input_bab1_content(pilih_tipe)
        list_gbr, path_gambar_utama, counter_gbr_bab1 = self._input_bab1_gambar(
            doc,
            counter_gbr_bab1,
        )
        analisa = self._input_bab1_analisa(
            pilih_tipe,
            isi_a,
            path_gambar_utama,
            pilihan_tpl,
            ai_client,
        )

        return (
            {
                "judul_sub_bab": judul_sub,
                "label_point_a": label_a,
                "isi_point_a": isi_a,
                "list_gambar": list_gbr,
                "isi_analisa": analisa,
                "list_kode": list_kode_final,
            },
            counter_gbr_bab1,
        )

    def _input_tugas_gambar(self, doc, counter_gbr_bab2):
        list_gbr_tgs = []
        if input("   Ada gambar? (y/n): ").lower() != "y":
            return list_gbr_tgs, counter_gbr_bab2

        while True:
            path = input(f"     File Gambar (utk Gambar 2.{counter_gbr_bab2}): ")
            obj = self.image_helper.muat_gambar(doc, path)
            if obj:
                cap = input("     Caption: ")
                list_gbr_tgs.append(
                    {
                        "objek_gambar": obj,
                        "caption": cap,
                        "nomor_tampil": counter_gbr_bab2,
                    }
                )
                counter_gbr_bab2 += 1
            if input("     Lagi? (y/n): ").lower() != "y":
                break

        return list_gbr_tgs, counter_gbr_bab2

    def _input_tugas_item(self, doc, nomor_tugas, counter_gbr_bab2):
        print(f"\n   >>> Tugas No. {nomor_tugas}")
        judul_tgs = input("   Topik Tugas: ")
        soal_txt = self.input_reader.input_multiline("   Masukkan Soal")
        jawab_txt = self.input_reader.input_multiline("   Masukkan Jawaban")

        list_gbr_tgs, counter_gbr_bab2 = self._input_tugas_gambar(doc, counter_gbr_bab2)
        return (
            {
                "judul_sub_bab": judul_tgs,
                "isi_soal": soal_txt,
                "isi_jawaban": jawab_txt,
                "ada_gambar": len(list_gbr_tgs) > 0,
                "list_gambar": list_gbr_tgs,
            },
            counter_gbr_bab2,
        )

    def input_bab1(self, doc, pilihan_tpl, ai_client):
        print("\n--- [BAGIAN 2] BAB 1 HASIL PRAKTIKUM ---")
        daftar_sub_bab1 = []
        nomor_sub = 1
        counter_gbr_bab1 = 1

        while True:
            item, counter_gbr_bab1 = self._input_bab1_sub_bab(
                doc,
                pilihan_tpl,
                ai_client,
                nomor_sub,
                counter_gbr_bab1,
            )
            daftar_sub_bab1.append(item)

            if input(f"\n   Lanjut ke Sub-Bab 1.{nomor_sub + 1}? (y/n): ").lower() != "y":
                break
            nomor_sub += 1

        return daftar_sub_bab1

    def input_bab2(self, doc):
        print("\n--- [BAGIAN 3] BAB 2 TUGAS PRAKTIKUM ---")
        daftar_tugas = []
        if input("Apakah ada Tugas di modul ini? (y/n): ").lower() == "y":
            nomor_tugas = 1
            counter_gbr_bab2 = 1
            while True:
                tugas_item, counter_gbr_bab2 = self._input_tugas_item(
                    doc,
                    nomor_tugas,
                    counter_gbr_bab2,
                )
                daftar_tugas.append(tugas_item)

                if input("   Tambah Tugas lagi? (y/n): ").lower() != "y":
                    break
                nomor_tugas += 1

        return daftar_tugas

    def input_bab3(self):
        print("\n--- [BAGIAN 4] BAB 3 KESIMPULAN ---")
        return self.input_reader.input_multiline("Masukkan Kesimpulan Laporan")
