import tkinter as tk
from tkinter import ttk


class CoverTab(ttk.Frame):
    def __init__(self, app, parent):
        super().__init__(parent, padding=30)
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

        group1 = ttk.LabelFrame(self, text=" Informasi Praktikum ", padding=15)
        group1.pack(fill="x", pady=(0, 20))

        fields1 = [
            ("Mata Kuliah", "mata_kuliah"),
            ("Nomor Modul", "nomor_modul"),
            ("Judul Modul", "judul"),
        ]

        for i, (label, key) in enumerate(fields1):
            ttk.Label(group1, text=label).grid(row=i, column=0, sticky="w", pady=8, padx=5)
            ttk.Entry(group1, textvariable=self.cover_vars[key], width=50).grid(
                row=i, column=1, sticky="ew", pady=8
            )

        group2 = ttk.LabelFrame(self, text=" Identitas Mahasiswa ", padding=15)
        group2.pack(fill="x", pady=(0, 20))

        fields2 = [
            ("Nama Lengkap", "nama"),
            ("NIM", "nim"),
            ("Tahun Akademik", "tahun"),
        ]

        for i, (label, key) in enumerate(fields2):
            ttk.Label(group2, text=label).grid(row=i, column=0, sticky="w", pady=8, padx=5)
            ttk.Entry(group2, textvariable=self.cover_vars[key], width=50).grid(
                row=i, column=1, sticky="ew", pady=8
            )

        group3 = ttk.LabelFrame(self, text=" Pengaturan Dokumen ", padding=15)
        group3.pack(fill="x")

        ttk.Label(group3, text="Pilih Gaya Laporan:").pack(side="left", padx=5)
        ttk.Radiobutton(
            group3, text="Gaya Rapat (V1)", variable=self.template_choice, value="1"
        ).pack(side="left", padx=15)
        ttk.Radiobutton(
            group3, text="Gaya Renggang (V2)", variable=self.template_choice, value="2"
        ).pack(side="left")

    def get_cover_data(self):
        return {key: var.get().strip() for key, var in self.cover_vars.items()}

    def get_template_choice(self):
        return self.template_choice.get()