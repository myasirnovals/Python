# Lab Report Generator Pro (LRG) 🚀

Aplikasi desktop berbasis Python (Tkinter + Google Gemini AI) untuk menyusun dan menghasilkan dokumen laporan praktikum (`.docx`) secara otomatis, terstruktur, rapi, dan sesuai dengan template standar.

---

## 📁 Struktur Direktori Proyek

Proyek ini menggunakan arsitektur modular berorientasi objek (OOP) yang memisahkan antarmuka (UI), logika bisnis (Services), integrasi AI, serta antarmuka baris perintah (CLI):

```text
DocumentGenerator_Laporan_Praktikum/
│
├── .env                         # Konfigurasi environment (API Key Gemini)
├── .gitignore                   # Konfigurasi file yang diabaikan git
├── LICENSE.md                   # Lisensi open-source proyek
├── main.spec                    # Konfigurasi packaging PyInstaller (.exe)
├── requirements.txt             # Daftar dependensi Python
├── REFACTORING_SUMMARY.md       # Catatan riwayat refactoring UI
├── README.md                    # Dokumentasi lengkap proyek
│
├── src/                         # Source code utama aplikasi
│   ├── main.py                  # Entry point utama aplikasi GUI
│   │
│   ├── assets/                  # Asset visual statis
│   │   └── logo.jpeg            # Logo aplikasi / kop laporan
│   │
│   ├── templates/               # Template dokumen Microsoft Word (.docx)
│   │   ├── format-1.docx        # Template Gaya Rapat (Indented Style)
│   │   ├── format-2.docx        # Template Gaya Renggang (Block Style)
│   │   └── format-3.docx        # Template Alternatif
│   │
│   ├── app/                     # Backend core logic & konfigurasi
│   │   ├── __init__.py          # Export komponen aplikasi
│   │   ├── ai_client.py         # Klien API Gemini (rotasi model, fallback, multimodal)
│   │   ├── config.py            # Loader variabel lingkungan (.env)
│   │   ├── doc_helpers.py       # Helper pemrosesan gambar & dokumen Word
│   │   ├── prompts.py           # Template prompt untuk analisis AI
│   │   │
│   │   ├── services/            # Layanan logika bisnis utama
│   │   │   ├── __init__.py
│   │   │   ├── analysis_service.py # Analisis kode, langkah kerja & kesimpulan via AI
│   │   │   └── report_service.py   # Rendering Jinja2 docxtpl, sanitasi XML, pembersihan & Word COM
│   │   │
│   │   └── cli/                 # Sub-paket untuk antarmuka terminal/CLI (opsional)
│   │       ├── __init__.py
│   │       ├── generator.py     # Generator interaktif berbasis konsol
│   │       ├── input_helpers.py # Helper input multiline di konsol
│   │       └── sections.py      # Pengumpul data bagian laporan via konsol
│   │
│   └── ui/                      # Lapisan antarmuka pengguna (Tkinter / ttk)
│       ├── __init__.py          # Export komponen UI
│       ├── constants.py         # Konstanta UI, dimensi, warna, ekstensi kode yang didukung
│       ├── utils.py             # Helper drag-and-drop, validasi file, screenshot
│       │
│       ├── core/                # Infrastruktur inti UI
│       │   ├── __init__.py
│       │   ├── app_window.py    # Jendela utama aplikasi & dynamic resource resolver
│       │   ├── base_tab.py      # Base class untuk seluruh tab
│       │   └── style_manager.py # Manajemen style & tema ttk
│       │
│       ├── components/          # Komponen UI modular
│       │   ├── __init__.py
│       │   └── code_image/      # Modul pengelolaan lampiran kode & tangkapan layar
│       │       ├── __init__.py
│       │       ├── code_image_tab.py  # Tab dasar reusable untuk Bab 1 & Bab 2
│       │       ├── items_mixin.py     # Mixin CRUD item sub-bab
│       │       ├── attachments_mixin.py # Mixin lampiran file & screenshot tool
│       │       ├── ai_mixin.py        # Mixin interaksi AI langsung dari editor
│       │       └── qa_mixin.py        # Mixin tanya-jawab (Q&A) tugas praktikum
│       │
│       └── tabs/                # Tab navigasi utama
│           ├── __init__.py
│           ├── cover_tab.py     # Tab informasi cover (Mata kuliah, Modul, Identitas)
│           ├── results_tab.py   # Tab Bab I: Hasil Praktikum
│           ├── tasks_tab.py     # Tab Bab II: Tugas Praktikum
│           ├── conclusion_tab.py# Tab Bab III: Kesimpulan (Manual / AI Generated)
│           └── generate_tab.py  # Tab Finalisasi & Export ke DOCX
```

---

## ⚙️ Persyaratan Sistem & Instalasi

### 1. Prasyarat
- **Python**: Versi 3.11 atau lebih baru (disarankan 3.11.x)
- **Sistem Operasi**: Windows 10/11 (mendukung auto-update TOC melalui Microsoft Word COM)
- **Microsoft Word** (opsional, untuk pembaruan Daftar Isi otomatis)

### 2. Pengaturan Virtual Environment
Buka terminal di root direktori proyek, lalu jalankan:

```bash
# Membuat virtual environment
python -m venv .venv

# Mengaktifkan virtual environment
.\.venv\Scripts\Activate.ps1   # PowerShell
# atau
.\.venv\Scripts\activate.bat   # Command Prompt
```

### 3. Instalasi Dependensi
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi API Key Gemini
Buat atau edit file `.env` di direktori root:
```env
GEMINI_API_KEY=AIzaSy... (API Key Anda)
```
*(Catatan: Anda juga dapat memasukkan API Key langsung melalui tombol AI KEY pada tab Cover aplikasi).*

---

## 🖥️ Cara Menjalankan Aplikasi

### Mode GUI (Rekomendasi)
Jalankan perintah berikut:
```bash
python src/main.py
```

### Mode CLI (Terminal)
Jika ingin menggunakan versi baris perintah klasik:
```bash
python -m app.cli.generator
```

---

## 📦 Kompilasi ke Executable (.EXE)

Aplikasi dapat dikompilasi menjadi executable standalone tanpa memerlukan instalasi Python di komputer pengguna menggunakan **PyInstaller**:

```bash
# Pastikan virtual environment aktif, lalu jalankan:
pyinstaller main.spec --noconfirm
```

Output `.exe` dan pustaka pendukung akan berada di folder:
```
dist/main/main.exe
```

---

## 🛡️ Catatan Teknis & Perbaikan Kualitas Dokumen

1. **Autoescape & Sanitasi XML**:
   Semua variabel teks (`<`, `>`, `&`) secara otomatis di-escape sebelum masuk ke template Jinja2 `docxtpl`, dan karakter kontrol ilegal XML (`\x00-\x08`, `\x0b`, `\x0c`, dll.) dibersihkan secara rekursif agar file `.docx` tidak pernah korup saat dibuka di Microsoft Word.
2. **Penanganan Baris Hantu (`##HAPUS##`)**:
   Penghapusan penanda `##HAPUS##` aman terhadap tabel Word dan tidak merusak struktur tabel atau cover.
3. **Pembersihan File Sementara**:
   Gambar yang diubah ukurannya selama perenderan disimpan secara sementara dan langsung dibersihkan otomatis setelah dokumen disimpan.
4. **Crash Logging**:
   Jika terjadi kesalahan tak terduga saat aplikasi berjalan dalam mode `.exe`, detail traceback lengkap akan dicatat secara otomatis ke file `crash.log` di direktori yang sama dengan executable.

