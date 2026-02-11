# Lab Report Generator - creates formatted practicum reports from user input.
# Copyright (C) 2026 Muhamad Yasir Noval
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact: myasirnoval23@if.unjani.ac.id

import os
import time
import json
import base64
import requests
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from dotenv import load_dotenv

load_dotenv()

# ================================================================
# 1. KONFIGURASI AI (MESIN GEMINI DIRECT API)
# ================================================================
# ⚠️ Gunakan API Key Google Anda yang sudah berhasil tadi
API_KEY = os.getenv("GEMINI_API_KEY")

# Variabel Global untuk menyimpan nama model
MODEL_NAME = None

# ================================================================
# 2. FUNGSI AI (DARI SCRIPT GEMINI YANG SUKSES)
# ================================================================
def dapatkan_model_aktif():
    """Mencari model Gemini yang HIDUP di akun Anda."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    print("\n🔍 Sedang mencari model AI yang aktif...")
    try:
        resp = requests.get(url)
        data = resp.json()
        if 'error' in data:
            print(f"❌ Error API Key: {data['error']['message']}")
            return None
            
        calon_model = []
        for m in data.get('models', []):
            nama = m['name'].replace("models/", "")
            if "gemini" in nama and "embedding" not in nama:
                calon_model.append(nama)

        model_pilihan = None
        # Cari yang 'flash' dulu
        for m in calon_model:
            if "flash" in m:
                model_pilihan = m
                break
        
        # Kalau gak ada, ambil sembarang
        if not model_pilihan and calon_model:
            model_pilihan = calon_model[0]

        if model_pilihan:
            print(f"✅ Sistem Siap! Menggunakan Otak: {model_pilihan}")
            return model_pilihan
        else:
            print("❌ Tidak ada model Gemini yang ditemukan.")
            return None
    except Exception as e:
        print(f"❌ Gagal koneksi internet: {e}")
        return None

def tanya_ai(prompt_text, path_gambar=None):
    global MODEL_NAME
    if not MODEL_NAME:
        MODEL_NAME = dapatkan_model_aktif()
        if not MODEL_NAME: return "Error: Tidak ada model."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    parts = [{"text": prompt_text}]
    
    # Handle Gambar
    if path_gambar and os.path.exists(path_gambar):
        try:
            with open(path_gambar, "rb") as f:
                b64_data = base64.b64encode(f.read()).decode('utf-8')
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg", 
                        "data": b64_data
                    }
                })
        except Exception as e:
            print(f"⚠️ Gagal baca gambar: {e}")

    payload = {"contents": [{"parts": parts}]}

    # Retry Logic (Anti-429)
    for i in range(5):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                try:
                    teks_hasil = response.json()['candidates'][0]['content']['parts'][0]['text']
                    
                    # --- MEMBERSIHKAN TANDA KUTIP & BACKTICK ---
                    # Ini akan membuang tanda ' dan ` dari istilah teknis
                    teks_bersih = teks_hasil.replace("'", "").replace("`", "").strip()

                    # 2. FILTER ANTI BASA-BASI (Hapus kalimat pembuka AI)
                    baris = teks_bersih.split('\n')
                    # Jika baris pertama mengandung kata kunci basa-basi, hapus!
                    if len(baris) > 0:
                        kata_kunci = ["berikut adalah", "analisa:", "penjelasan:", "berdasarkan gambar"]
                        baris_pertama_lower = baris[0].lower()
                        
                        # Cek apakah baris pertama itu cuma pengantar?
                        if any(k in baris_pertama_lower for k in kata_kunci) or baris[0].strip().endswith(":"):
                            # Kita buang baris pertama, ambil sisanya
                            baris = baris[1:]
                    
                    # Gabungkan lagi (Hanya pakai \n satu kali agar RAPAT)
                    # strip() membuang spasi kosong di awal/akhir sisa teks
                    teks_final = "\n".join(baris).strip()
                    
                    return teks_final
                except:
                    return "Error: Format jawaban aneh."
            elif response.status_code == 429:
                wait = (i + 1) * 5
                print(f"      ⏳ Server sibuk, menunggu {wait} detik...")
                time.sleep(wait)
            elif response.status_code == 404:
                print("      🔄 Model hilang, mencari ulang...")
                MODEL_NAME = dapatkan_model_aktif()
                if not MODEL_NAME: return "Gagal: Model hilang."
            else:
                return f"Gagal API: {response.status_code}"
        except Exception as e:
            time.sleep(2)

    return "Gagal: Server busy (Give up)."

# ================================================================
# 3. FUNGSI BANTUAN (DARI SCRIPT GROQ - LEBIH RAPI)
# ================================================================
def muat_gambar(doc, path, lebar_mm=120):
    if os.path.exists(path):
        return InlineImage(doc, path, width=Mm(lebar_mm))
    else:
        if path.strip() != "":
            print(f"⚠️  File gambar '{path}' tidak ditemukan.")
        return ""

def input_multiline(label):
    print(f"{label} (Tekan Enter 2x jika selesai):")
    lines = []
    while True:
        line = input()
        if line:
            lines.append(line)
        else:
            break
    return "\n".join(lines)

# ================================================================
# 4. PROGRAM UTAMA (STRUKTUR GROQ + OTAK GEMINI)
# ================================================================
def main():
    # --- PILIH TEMPLATE ---
    print("\n--- PILIH GAYA FORMAT LAPORAN ---")
    print(" [1] Gaya Rapat (Menjorok 0.7cm, Antar paragraf rapat)")
    print(" [2] Gaya Renggang (Rata Kiri, Antar paragraf ada jarak)")
    pilihan_tpl = input("Pilih (1/2): ")

    if pilihan_tpl == "2":
        nama_template = "format-2.docx"
        print("👉 Menggunakan: Template Renggang (Block Style)")
    else:
        nama_template = "format-1.docx"
        print("👉 Menggunakan: Template Rapat (Indented Style)")

    if not os.path.exists(nama_template):
        print(f"❌ Error: File '{nama_template}' tidak ditemukan!")
        print("   Pastikan Anda sudah membuat 2 file template sesuai panduan.")
        return

    # Cek Koneksi AI di awal
    global MODEL_NAME
    MODEL_NAME = dapatkan_model_aktif()
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
    judul       = input("Judul Modul : ").upper()
    nama        = input("Nama        : ").upper()
    nim         = input("NIM         : ")
    tahun       = input("Tahun       : ")

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
        if pilih_tipe == "2":
            label_a = "Langkah Kerja"
            isi_a = input_multiline("   Masukkan Langkah Kerja")
        else:
            label_a = "Source Code"
            # --- LOGIKA INPUT MULTI-FILE ---
            data_kode_mentah = [] 
            counter_kode = 1
            
            print("   [Input Source Code]")
            while True:
                print(f"\n     --- File Kode ke-{counter_kode} ---")
                nama_file = input("     Nama File (misal: Main.java): ")
                print(f"     Paste isi kode '{nama_file}' di bawah:")
                isi_mentah = input_multiline("     Isi Kode")
                
                data_kode_mentah.append({
                    'nama': nama_file,
                    'isi': isi_mentah
                })
                counter_kode += 1
                if input("     Tambah file kode lagi? (y/n): ").lower() != 'y': break
            
            # --- PERSIAPAN DATA UNTUK TEMPLATE ---
            # Kita buat list khusus bernama 'list_kode_final'
            list_kode_final = []
            
            if len(data_kode_mentah) > 0:
                for i, d in enumerate(data_kode_mentah, 1):
                    # Jika file cuma 1, judul kosongkan. Jika banyak, beri nomor.
                    if len(data_kode_mentah) > 1:
                        judul_tampil = f"{i}. {d['nama']}"
                    else:
                        judul_tampil = "" # Kosong karena cuma 1 file (sesuai request)
                        
                    list_kode_final.append({
                        'judul': judul_tampil,
                        'isi': d['isi']
                    })
            
            # isi_a dikosongkan saja atau diisi dummy, karena kita pakai list_kode_final
            isi_a = ""

        # Input Gambar
        list_gbr = []
        path_gambar_utama = "" # Untuk dikirim ke AI
        
        print(f"   [Input Gambar Hasil]")
        while True:
            path = input(f"     File Gambar (utk Gambar 1.{counter_gbr_bab1}): ")
            if not path: break
            
            if not path_gambar_utama: path_gambar_utama = path # Ambil gambar pertama buat AI
            
            obj = muat_gambar(doc, path)
            if obj:
                cap = input("     Caption: ")
                list_gbr.append({'objek_gambar': obj, 'caption': cap, 'nomor_tampil': counter_gbr_bab1})
                counter_gbr_bab1 += 1
            
            if input("     Tambah gambar lagi? (y/n): ").lower() != 'y': break

        # --- LOGIKA AI (GEMINI) ---
        analisa = ""
        print("\n   [Input Analisa]")
        if input("   🤖 Gunakan AI untuk analisa? (y/n): ").lower() == 'y':
            
            # --- UPDATE: INSTRUKSI GAYA (YANG GALAK & TEGAS) ---
            instruksi_gaya = """
            ATURAN WAJIB (JANGAN DILANGGAR):
            1. LANGSUNG KE INTI. DILARANG KERAS menggunakan kalimat pembuka seperti "Berikut adalah analisa...", "Berdasarkan gambar...", atau "Analisa:".
            2. Mulailah langsung dengan kata pertama dari paragraf 1.
            3. Buat TEPAT 2 PARAGRAF.
            4. Gunakan Bahasa Indonesia Formal yang akademis & padat ("daging").
            5. JANGAN gunakan tanda kutip satu (') atau backtick (`) pada istilah teknis.
            6. Pisahkan antar paragraf dengan SATU KALI ENTER saja.
            """

            # Tentukan Prompt berdasarkan Tipe
            if pilih_tipe == "1": # Source Code
                prompt = f"""
                Analisa Laporan Praktikum Pemrograman.
                KODE PROGRAM:
                {isi_a}
                
                TUGAS:
                Lihat gambar output yang dilampirkan, lalu jelaskan bagaimana kode di atas bekerja menghasilkan output tersebut.
                
                {instruksi_gaya}
                """
            else: # Langkah Kerja
                prompt = f"""
                Analisa Langkah Kerja Praktikum.
                
                TUGAS:
                Lihat screenshot yang dilampirkan. Jelaskan proses apa yang sedang dilakukan user di layar tersebut dan apa fungsi dari menu/tombol yang terlihat.
                
                Info Tambahan User: {isi_a}
                
                {instruksi_gaya}
                """
            
            # Panggil Fungsi Sakti Gemini
            analisa = tanya_ai(prompt, path_gambar_utama)
            # --- PERBAIKAN FORMATTING MANUAL (THE FIX) ---
            # Jika Format 1 (Rapat), kita suntikkan TAB (\t) manual
            # karena Word menganggap \n sebagai "Soft Enter".
            if pilihan_tpl == "1" and analisa:
                # 1. Tambahkan Tab di awal paragraf pertama
                analisa = analisa.replace("\n\n", "\n")
                
                # 2. SUNTIKKAN TAB (Indentasi)
                # Tambah Tab di awal, dan Tab setelah setiap ganti baris
                analisa = "\t" + analisa.replace("\n", "\n\t")
                
            print(f"   ✅ Hasil AI: Selesai ({len(analisa)} karakter)")
        else:
            analisa = input_multiline("   Masukkan Analisa Manual")

        daftar_sub_bab1.append({
            'judul_sub_bab': judul_sub, 'label_point_a': label_a,
            'isi_point_a': isi_a, 'list_gambar': list_gbr, 'isi_analisa': analisa,
            'list_kode': list_kode_final
        })

        if input(f"\n   Lanjut ke Sub-Bab 1.{nomor_sub+1}? (y/n): ").lower() != 'y': break
        nomor_sub += 1

    # 3. INPUT BAB 2 (TUGAS PRAKTIKUM) - DARI SCRIPT GROQ
    print("\n--- [BAGIAN 3] BAB 2 TUGAS PRAKTIKUM ---")
    daftar_tugas = []
    if input("Apakah ada Tugas di modul ini? (y/n): ").lower() == 'y':
        nomor_tugas = 1
        counter_gbr_bab2 = 1
        while True:
            print(f"\n   >>> Tugas No. {nomor_tugas}")
            judul_tgs = input(f"   Topik Tugas: ")
            soal_txt = input_multiline("   Masukkan Soal")
            jawab_txt = input_multiline("   Masukkan Jawaban")
            
            list_gbr_tgs = []
            if input("   Ada gambar? (y/n): ").lower() == 'y':
                while True:
                    path = input(f"     File Gambar (utk Gambar 2.{counter_gbr_bab2}): ")
                    obj = muat_gambar(doc, path)
                    if obj:
                        cap = input("     Caption: ")
                        list_gbr_tgs.append({'objek_gambar': obj, 'caption': cap, 'nomor_tampil': counter_gbr_bab2})
                        counter_gbr_bab2 += 1
                    if input("     Lagi? (y/n): ").lower() != 'y': break
            
            daftar_tugas.append({
                'judul_sub_bab': judul_tgs, 'isi_soal': soal_txt,
                'isi_jawaban': jawab_txt, 'ada_gambar': (len(list_gbr_tgs) > 0),
                'list_gambar': list_gbr_tgs
            })
            
            if input(f"   Tambah Tugas lagi? (y/n): ").lower() != 'y': break
            nomor_tugas += 1

    # 4. INPUT BAB 3 (KESIMPULAN) - DARI SCRIPT GROQ
    print("\n--- [BAGIAN 4] BAB 3 KESIMPULAN ---")
    isi_kesimpulan = input_multiline("Masukkan Kesimpulan Laporan")

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
        doc.render(context)
        doc.save(nama_file)
        print(f"✅ BERHASIL! File tersimpan: {nama_file}")
    except Exception as e:
        print(f"❌ Gagal render: {e}")

if __name__ == "__main__":
    main()