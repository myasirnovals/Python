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

from docxtpl import DocxTemplate

from app.ai_client import GeminiClient
from app.sections import input_bab1, input_bab2, input_bab3, input_cover, pilih_template

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# ================================================================
# PROGRAM UTAMA (STRUKTUR GROQ + OTAK GEMINI)
# ================================================================
def main():
    # --- PILIH TEMPLATE ---
    pilihan_tpl, nama_template = pilih_template(TEMPLATES_DIR)

    if not os.path.exists(nama_template):
        print(f"❌ Error: File '{nama_template}' tidak ditemukan!")
        print("   Pastikan Anda sudah membuat 2 file template sesuai panduan.")
        return

    # Cek Koneksi AI di awal
    ai_client = GeminiClient()
    if not ai_client.get_active_model():
        print("⛔ Program berhenti karena AI tidak bisa connect.")
        return

    doc = DocxTemplate(nama_template)
    print("\n==============================================")
    print("   GENERATOR LAPORAN HYBRID (Structure + AI)  ")
    print("==============================================")

    # 1. INPUT DATA COVER
    cover = input_cover()

    # 2. INPUT BAB 1 (HASIL PRAKTIKUM)
    daftar_sub_bab1 = input_bab1(doc, pilihan_tpl, ai_client)

    # 3. INPUT BAB 2 (TUGAS PRAKTIKUM) - DARI SCRIPT GROQ
    daftar_tugas = input_bab2(doc)

    # 4. INPUT BAB 3 (KESIMPULAN) - DARI SCRIPT GROQ
    isi_kesimpulan = input_bab3()

    # 5. RENDER & SAVE
    print("\n--- MENYIMPAN FILE... ---")
    context = {
        **cover,
        "daftar_sub_bab": daftar_sub_bab1,
        "daftar_tugas": daftar_tugas,
        "isi_kesimpulan": isi_kesimpulan,
    }

    try:
        nama_file = (
            f"Laporan_Modul_{cover['nomor_modul']}_{cover['nama'].replace(' ', '_')}.docx"
        )
        doc.render(context)
        doc.save(nama_file)
        print(f"✅ BERHASIL! File tersimpan: {nama_file}")
    except Exception as e:
        print(f"❌ Gagal render: {e}")

if __name__ == "__main__":
    main()