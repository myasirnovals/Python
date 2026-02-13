from tkinter import ttk

def build_generate_tab(app, parent):
    frame = ttk.Frame(parent, padding=40)
    frame.pack(fill="both", expand=True)

    center_frame = ttk.Frame(frame)
    center_frame.place(relx=0.5, rely=0.4, anchor="center")

    ttk.Label(
        center_frame, 
        text="Laporan Anda Sudah Siap!", 
        font=("Segoe UI", 16, "bold")
    ).pack(pady=10)
    
    ttk.Label(
        center_frame, 
        text="Pastikan semua data di tab sebelumnya sudah diisi dengan benar.",
        foreground="#666666"
    ).pack(pady=(0, 30))

    # Tombol Generate Besar
    gen_btn = ttk.Button(
        center_frame, 
        text="🚀 GENERATE LAPORAN (.DOCX)", 
        style="Action.TButton",
        command=app._generate
    )
    gen_btn.pack(ipadx=20, ipady=10)

    ttk.Label(
        center_frame, 
        text="File akan disimpan secara otomatis setelah Anda memilih lokasi penyimpanan.",
        font=("Segoe UI", 8),
        foreground="#999999"
    ).pack(pady=20)