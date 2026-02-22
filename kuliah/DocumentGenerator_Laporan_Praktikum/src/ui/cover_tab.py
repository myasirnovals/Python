import tkinter as tk
from tkinter import ttk

class CoverTab(ttk.Frame):
    def __init__(self, app, parent):
        # Padding luar 20
        super().__init__(parent, padding=20) 
        self.app = app
        self.cover_vars = {
            "mata_kuliah": tk.StringVar(),
            "nomor_modul": tk.StringVar(),
            "judul": tk.StringVar(),
            "nama": tk.StringVar(),
            "nim": tk.StringVar(),
            "tahun": tk.StringVar(),
        }
        self.template_choice = tk.StringVar(value="1")
        self._build()

    def _build(self):
        self.pack(fill="both", expand=True)

        # --- GROUP 1: INFORMASI PRAKTIKUM ---
        group1 = ttk.LabelFrame(self, text=" Informasi Praktikum ", padding=15)
        group1.pack(fill="x", pady=(0, 15)) 
        group1.columnconfigure(1, weight=1)

        fields1 = [("Mata Kuliah", "mata_kuliah"), ("Nomor Modul", "nomor_modul"), ("Judul Modul", "judul")]
        for i, (label, key) in enumerate(fields1):
            ttk.Label(group1, text=label).grid(row=i, column=0, sticky="w", pady=8, padx=(0, 15))
            ttk.Entry(group1, textvariable=self.cover_vars[key]).grid(row=i, column=1, sticky="ew", pady=8)

        # --- GROUP 2: IDENTITAS MAHASISWA ---
        group2 = ttk.LabelFrame(self, text=" Identitas Mahasiswa ", padding=15)
        group2.pack(fill="x", pady=(0, 15)) 
        group2.columnconfigure(1, weight=1)

        fields2 = [("Nama Lengkap", "nama"), ("NIM", "nim"), ("Tahun Akademik", "tahun")]
        for i, (label, key) in enumerate(fields2):
            ttk.Label(group2, text=label).grid(row=i, column=0, sticky="w", pady=8, padx=(0, 15))
            ttk.Entry(group2, textvariable=self.cover_vars[key]).grid(row=i, column=1, sticky="ew", pady=8)

        # --- GROUP 3: PENGATURAN DOKUMEN (CENTERED FIX) ---
        # Kita gunakan padding yang seimbang (20px semua sisi)
        group3 = ttk.LabelFrame(self, text=" Pengaturan Dokumen ", padding=20)
        group3.pack(fill="x", pady=(0, 5)) 
        
        # KONFIGURASI AGAR PRESISI DI TENGAH
        group3.columnconfigure(1, weight=1)
        group3.columnconfigure(2, weight=1)
        # Baris 0 kita set weight=1 agar ia mengambil ruang vertikal yang tersedia & memusatkan isinya
        group3.rowconfigure(0, weight=1) 

        # Catatan: Saya HAPUS 'pady' pada widget di bawah ini.
        # Kita serahkan pengaturan jarak sepenuhnya pada padding frame (group3) 
        # supaya posisinya benar-benar di tengah (center gravity).

        # Label
        ttk.Label(group3, text="Pilih Gaya Laporan:").grid(
            row=0, column=0, sticky="w", padx=(0, 10) # pady dihapus
        )
        
        # Radio Button 1
        ttk.Radiobutton(
            group3, text="Nur Faid Prasetyo", variable=self.template_choice, value="1"
        ).grid(
            row=0, column=1, sticky="w", padx=5 # pady dihapus
        )
        
        # Radio Button 2
        ttk.Radiobutton(
            group3, text="Astriani Komeri", variable=self.template_choice, value="2"
        ).grid(
            row=0, column=2, sticky="w", padx=5 # pady dihapus
        )

    def get_cover_data(self):
        return {key: var.get().strip() for key, var in self.cover_vars.items()}

    def get_template_choice(self):
        return self.template_choice.get()

    def fill_test_data(self):
        self.cover_vars["mata_kuliah"].set("Pemrograman Dasar")
        self.cover_vars["nomor_modul"].set("03")
        self.cover_vars["judul"].set("Percabangan dan Perulangan")
        self.cover_vars["nama"].set("Budi Santoso")
        self.cover_vars["nim"].set("2201234567")
        self.cover_vars["tahun"].set("2025/2026")
        self.template_choice.set("1")