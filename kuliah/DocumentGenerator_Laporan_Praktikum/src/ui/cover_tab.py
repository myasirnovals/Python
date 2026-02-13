from tkinter import ttk

def build_cover_tab(app, parent):
    container = ttk.Frame(parent, padding=30)
    container.pack(fill="both", expand=True)

    # Section 1: Detail Praktikum
    group1 = ttk.LabelFrame(container, text=" Informasi Praktikum ", padding=15)
    group1.pack(fill="x", pady=(0, 20))

    fields1 = [
        ("Mata Kuliah", "mata_kuliah"),
        ("Nomor Modul", "nomor_modul"),
        ("Judul Modul", "judul")
    ]

    for i, (label, key) in enumerate(fields1):
        ttk.Label(group1, text=label).grid(row=i, column=0, sticky="w", pady=8, padx=5)
        ttk.Entry(group1, textvariable=app.cover_vars[key], width=50).grid(row=i, column=1, sticky="ew", pady=8)

    # Section 2: Identitas Mahasiswa
    group2 = ttk.LabelFrame(container, text=" Identitas Mahasiswa ", padding=15)
    group2.pack(fill="x", pady=(0, 20))

    fields2 = [
        ("Nama Lengkap", "nama"),
        ("NIM", "nim"),
        ("Tahun Akademik", "tahun")
    ]

    for i, (label, key) in enumerate(fields2):
        ttk.Label(group2, text=label).grid(row=i, column=0, sticky="w", pady=8, padx=5)
        ttk.Entry(group2, textvariable=app.cover_vars[key], width=50).grid(row=i, column=1, sticky="ew", pady=8)

    # Section 3: Format Template
    group3 = ttk.LabelFrame(container, text=" Pengaturan Dokumen ", padding=15)
    group3.pack(fill="x")

    ttk.Label(group3, text="Pilih Gaya Laporan:").pack(side="left", padx=5)
    ttk.Radiobutton(group3, text="Gaya Rapat (V1)", variable=app.template_choice, value="1").pack(side="left", padx=15)
    ttk.Radiobutton(group3, text="Gaya Renggang (V2)", variable=app.template_choice, value="2").pack(side="left")