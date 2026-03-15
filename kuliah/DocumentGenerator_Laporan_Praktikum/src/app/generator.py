"""Porting lengkap dari generator_laporan.py — CLI generator laporan."""
import os
import time
from docxtpl import DocxTemplate, RichText, InlineImage
from docx import Document
from docx.shared import Mm

from . import ai_client, doc_helpers, input_helpers, config


def main():
    # --- PILIH TEMPLATE ---
    print("\n--- PILIH GAYA FORMAT LAPORAN ---")
    print(" [1] Gaya Rapat (Menjorok 0.7cm, Antar paragraf rapat)")
    print(" [2] Gaya Renggang (Rata Kiri, Antar paragraf ada jarak)")
    pilihan_tpl = input("Pilih (1/2): ")

    if pilihan_tpl == "2":
        nama_template = "templates/format-2.docx"
        print("👉 Menggunakan: Template Renggang (Block Style)")
    else:
        nama_template = "templates/format-1.docx"
        print("👉 Menggunakan: Template Rapat (Indented Style)")

    if not os.path.exists(nama_template):
        print(f"❌ Error: File '{nama_template}' tidak ditemukan!")
        print("   Pastikan Anda sudah membuat 2 file template sesuai panduan.")
        return

    # Cek Koneksi AI di awal
    MODEL_NAME = ai_client.dapatkan_model_aktif()
    if not MODEL_NAME:
        print("⛔ Program berhenti karena AI tidak bisa connect.")
        return

    doc = DocxTemplate(nama_template)
    print("\n==============================================")
    print("   GENERATOR LAPORAN HYBRID (Structure + AI)  ")
    print("==============================================")

    # 1. INPUT DATA COVER
    print("\n--- [BAGIAN 1] DATA COVER ---")
    mata_kuliah = input("Mata Kuliah : ").upper()
    nomor_modul = input("Nomor Modul : ")
    judul = input("Judul Modul : ").upper()
    nama = input("Nama        : ").upper()
    nim = input("NIM         : ")
    tahun = input("Tahun       : ")

    # --- TAMBAHAN BARU: INPUT FILE MODUL ---
    print("\n   [OPSIONAL] File Modul Praktikum (PDF/Word)")
    path_modul = input("   Path File Modul (Kosongkan jika tidak ada): ")

    isi_teks_modul = ""
    if path_modul.strip():
        print("   📖 Sedang membaca isi modul...")
        isi_teks_modul = doc_helpers.baca_isi_modul(path_modul)
        if isi_teks_modul:
            print(f"   ✅ Modul berhasil dimuat! ({len(isi_teks_modul)} karakter)")
        else:
            print("   ⚠️ Modul kosong atau gagal dibaca.")

    # 2. INPUT BAB 1 (HASIL PRAKTIKUM)
    print("\n--- [BAGIAN 2] BAB 1 HASIL PRAKTIKUM ---")
    daftar_sub_bab1 = []
    nomor_sub = 1
    counter_gbr_bab1 = 1

    while True:
        print(f"\n   >>> Sub-Bab 1.{nomor_sub}")
        judul_sub = input(f"   Judul Sub-Bab: ")

        print("   Tipe Point A: [1] Source Code  [2] Langkah Kerja")
        pilih_tipe = input("   Pilih (1/2): ")

        isi_a = ""
        label_a = ""
        list_kode_final = []
        if pilih_tipe == "2":
            label_a = "Langkah Kerja"
            print("\n   [Input Langkah Kerja]")

            raw_isi = ""
            pakai_ai = input("   🤖 Gunakan AI untuk buat langkah kerja? (y/n): ").lower()

            if pakai_ai == 'y':
                print("      ⏳ Sedang berpikir...")

                instruksi_kualitas = """
                ATURAN KUALITAS & KUANTITAS:
                1. WAJIB HASILKAN ANTARA MINIMAL 7 SAMPAI MAKSIMAL 12 BARIS LANGKAH.
                2. Jika langkah asli terlalu sedikit (<7): Pecah langkah kompleks menjadi lebih detail.
                3. Jika langkah asli terlalu banyak (>12): Gabungkan langkah-langkah kecil/remeh menjadi satu baris.
                4. ISI HARUS PADAT & TEKNIS: Hindari kalimat "Buka aplikasi" saja. Gunakan "Buka IntelliJ IDEA dan tunggu loading selesai".
                5. DILARANG memasukkan langkah sampah seperti "Siapkan PC", "Berdoa", atau "Selesai". Langsung ke teknis.
                6. JANGAN PAKAI NOMOR (1. 2. 3.) dan Bullet Points (*, -, •). Python yang akan memberi nomor nanti.
                """

                # SKENARIO 1: PRIORITAS MODUL (Jika ada file modul)
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
                    raw_isi = ai_client.tanya_ai(prompt_langkah)

                # SKENARIO 2: PRIORITAS GAMBAR (Jika modul tidak ada)
                else:
                    print("      ⚠️ Tidak ada file modul. AI akan melihat dari screenshot.")
                    path_sementara = input(f"      Masukkan path gambar untuk dianalisa: ").replace('"', '')

                    if path_sementara and os.path.exists(path_sementara):
                        prompt_langkah = f"""
                        Peran: Asisten Lab Komputer.
                        Tugas: Buat simulasi Langkah Kerja berdasarkan Screenshot ini.

                        Instruksi Analisa:
                        1. Lihat UI/Codingan di gambar.
                        2. Rekonstruksi urutan langkah logis (step-by-step) yang dilakukan user untuk mencapai hasil di gambar tersebut.

                        {instruksi_kualitas}
                        """
                        raw_isi = ai_client.tanya_ai(prompt_langkah, path_sementara)
                    else:
                        print("      ❌ Gambar tidak ditemukan. Beralih ke manual.")
                        raw_isi = ""

                if raw_isi and "Gagal" not in raw_isi:
                    print("      ✅ Langkah Kerja dari AI siap! (Format akan otomatis dirapikan)")
                else:
                    print("      ⚠️ AI tidak bisa menjawab. Silakan ketik manual.")
                    raw_isi = input_helpers.input_multiline("   Masukkan Langkah Kerja")

            else:
                print("   (Ketik langkah per baris, Python akan memberi nomor otomatis)")
                raw_isi = input_helpers.input_multiline("   Masukkan Langkah Kerja")

            if not raw_isi:
                raw_isi = "Langkah kerja tidak diisi."

            lines = raw_isi.split('\n')
            list_bernomor = []
            nomor_urut = 1

            for baris in lines:
                teks = baris.strip()
                teks_bersih = teks.lstrip(' *-•.1234567890').strip()
                if teks_bersih:
                    if nomor_urut == 1:
                        item_baru = f"\u200B{nomor_urut}. {teks_bersih}"
                    else:
                        item_baru = f" {nomor_urut}. {teks_bersih}"
                    list_bernomor.append(item_baru)
                    nomor_urut += 1

            isi_a = "\n".join(list_bernomor) + "\n"
        else:
            label_a = "Source Code"
            data_kode_mentah = []
            counter_kode = 1

            print("   [Input Source Code]")
            while True:
                print(f"\n     --- File Kode ke-{counter_kode} ---")
                nama_file = input("     Nama File (misal: Main.java): ")
                print(f"     Paste isi kode '{nama_file}' di bawah:")
                isi_mentah = input_helpers.input_multiline("     Isi Kode")

                data_kode_mentah.append({'nama': nama_file, 'isi': isi_mentah})
                counter_kode += 1
                if input("     Tambah file kode lagi? (y/n): ").lower() != 'y':
                    break

            if len(data_kode_mentah) > 0:
                for i, d in enumerate(data_kode_mentah, 1):
                    if len(data_kode_mentah) > 1:
                        prefix = "\n" if i > 1 else ""
                        teks_judul = f"{prefix}{i}. {d['nama']}"
                        judul_tampil = RichText(teks_judul)
                    else:
                        judul_tampil = "##HAPUS##"

                    list_kode_final.append({'judul': judul_tampil, 'isi': d['isi']})

            temp_list_ai = []
            for d in data_kode_mentah:
                temp_list_ai.append(f"File: {d['nama']}\n{d['isi']}")
            isi_a = "\n\n".join(temp_list_ai)

        # Input Gambar
        list_gbr = []
        path_gambar_utama = ""

        print(f"   [Input Gambar Hasil]")
        while True:
            path = input(f"     File Gambar (utk Gambar 1.{counter_gbr_bab1}): ")
            if not path:
                break

            if not path_gambar_utama:
                path_gambar_utama = path

            obj = doc_helpers.muat_gambar(doc, path)
            if obj:
                cap = input("     Caption: ")
                caption_fix = cap + "\n"
                list_gbr.append({'objek_gambar': obj, 'caption': caption_fix, 'nomor_tampil': counter_gbr_bab1})
                counter_gbr_bab1 += 1

            if input("     Tambah gambar lagi? (y/n): ").lower() != 'y':
                break

        # --- LOGIKA AI (GEMINI) ---
        analisa = ""
        print("\n   [Input Analisa]")
        if input("   🤖 Gunakan AI untuk analisa? (y/n): ").lower() == 'y':
            instruksi_gaya = """
            ATURAN WAJIB (JANGAN DILANGGAR):
            1. LANGSUNG KE INTI. DILARANG KERAS menggunakan kalimat pembuka seperti "Berikut adalah analisa...", "Berdasarkan gambar...", atau "Analisa:".
            2. Mulailah langsung dengan kata pertama dari paragraf 1.
            3. Buat TEPAT 2 PARAGRAF.
            4. Gunakan Bahasa Indonesia Formal yang akademis & padat ("daging").
            5. JANGAN gunakan tanda kutip satu (') atau backtick (`) pada istilah teknis.
            6. Pisahkan antar paragraf dengan SATU KALI ENTER saja.
            """

            if pilih_tipe == "1":
                prompt = f"""
                Analisa Laporan Praktikum Pemrograman.
                KODE PROGRAM:
                {isi_a}

                TUGAS:
                Lihat gambar output yang dilampirkan, lalu jelaskan bagaimana kode di atas bekerja menghasilkan output tersebut.

                {instruksi_gaya}
                """
            else:
                prompt = f"""
                Analisa Langkah Kerja Praktikum.

                TUGAS:
                Lihat screenshot yang dilampirkan. Jelaskan proses apa yang sedang dilakukan user di layar tersebut dan apa fungsi dari menu/tombol yang terlihat.

                Info Tambahan User: {isi_a}

                {instruksi_gaya}
                """

            analisa = ai_client.tanya_ai(prompt, path_gambar_utama)
            if pilihan_tpl == "1" and analisa:
                analisa = analisa.replace("\n\n", "\n")
                analisa = "\t" + analisa.replace("\n", "\n\t")

            print(f"   ✅ Hasil AI: Selesai ({len(analisa)} karakter)")
        else:
            analisa = input_helpers.input_multiline("   Masukkan Analisa Manual")
            if pilihan_tpl == "1" and analisa:
                analisa = analisa.replace("\n\n", "\n")
                analisa = "\t" + analisa.replace("\n", "\n\t")

        daftar_sub_bab1.append({
            'judul_sub_bab': judul_sub, 'label_point_a': label_a,
            'isi_point_a': isi_a, 'list_gambar': list_gbr, 'isi_analisa': analisa,
            'list_kode': list_kode_final
        })

        if input(f"\n   Lanjut ke Sub-Bab 1.{nomor_sub+1}? (y/n): ").lower() != 'y':
            break
        nomor_sub += 1

    # 3. INPUT BAB 2 (TUGAS PRAKTIKUM)
    print("\n--- [BAGIAN 3] BAB 2 TUGAS PRAKTIKUM ---")
    daftar_tugas = []
    if input("Apakah ada Tugas di modul ini? (y/n): ").lower() == 'y':
        nomor_tugas = 1
        counter_gbr_bab2 = 1
        while True:
            print(f"\n   >>> Tugas No. {nomor_tugas}")
            judul_tgs = input(f"   Topik Tugas: ")
            soal_txt = input_helpers.input_multiline("   Masukkan Soal")
            jawab_txt = input_helpers.input_multiline("   Masukkan Jawaban")

            list_gbr_tgs = []
            if input("   Ada gambar? (y/n): ").lower() == 'y':
                while True:
                    path = input(f"     File Gambar (utk Gambar 2.{counter_gbr_bab2}): ")
                    obj = doc_helpers.muat_gambar(doc, path)
                    if obj:
                        cap = input("     Caption: ")
                        list_gbr_tgs.append({'objek_gambar': obj, 'caption': cap + "\n", 'nomor_tampil': counter_gbr_bab2})
                        counter_gbr_bab2 += 1
                    if input("     Lagi? (y/n): ").lower() != 'y':
                        break

            daftar_tugas.append({
                'judul_sub_bab': judul_tgs, 'isi_soal': soal_txt,
                'isi_jawaban': jawab_txt, 'ada_gambar': (len(list_gbr_tgs) > 0),
                'list_gambar': list_gbr_tgs
            })

            if input(f"   Tambah Tugas lagi? (y/n): ").lower() != 'y':
                break
            nomor_tugas += 1

    # 4. INPUT BAB 3 (KESIMPULAN)
    print("\n--- [BAGIAN 4] BAB 3 KESIMPULAN ---")
    isi_kesimpulan = input_helpers.input_multiline("Masukkan Kesimpulan Laporan")

    # 5. RENDER & SAVE
    print("\n--- MENYIMPAN FILE... ---")
    context = {
        'mata_kuliah': mata_kuliah, 'nomor_modul': nomor_modul,
        'judul': judul, 'nama': nama, 'nim': nim, 'tahun': tahun,
        'daftar_sub_bab': daftar_sub_bab1,
        'daftar_tugas': daftar_tugas,
        'isi_kesimpulan': isi_kesimpulan
    }

    try:
        nama_file = f"Laporan_Modul_{nomor_modul}_{nama.replace(' ', '_')}.docx"
        doc.render(context, autoescape=True)
        doc.save(nama_file)
        print(f"✅ BERHASIL! File tersimpan: {nama_file}")

        # 1. Bersihkan baris hantu dulu
        doc_helpers.hapus_baris_hantu(nama_file)

        # 2. Update Daftar Isi otomatis
        doc_helpers.update_toc_word(nama_file)

        print(f"🎉 SELESAI! File {nama_file} sudah rapi & rapat.")
    except Exception as e:
        print(f"❌ Gagal render: {e}")


if __name__ == '__main__':
    main()


def render_report(template, context: dict, output_path: str, pilihan_tpl: str = "1"):
    """Render report given a template path or DocxTemplate and context, save to output_path.

    `template` may be a str path or a `DocxTemplate` instance. If DocxTemplate is
    provided, any `InlineImage` objects in `context` should have been created with
    the same document instance.
    """
    try:
        if isinstance(template, str):
            doc = DocxTemplate(template)
        else:
            doc = template

        doc.render(context, autoescape=True)
        doc.save(output_path)

        # Post-processing: remove ghost lines and update TOC
        try:
            doc_helpers.hapus_baris_hantu(output_path)
        except Exception:
            pass

        try:
            doc_helpers.update_toc_word(output_path)
        except Exception:
            pass

        return True, None
    except Exception as e:
        return False, str(e)
