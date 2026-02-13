import tkinter as tk
from tkinter import ttk

def build_bab2_tab(app, parent):
    frame = ttk.Frame(parent, padding=20)
    frame.pack(fill="both", expand=True)

    header_frame = ttk.Frame(frame)
    header_frame.pack(fill="x", pady=(0, 10))
    
    ttk.Label(header_frame, text="Daftar Tugas Praktikum", style="Header.TLabel").pack(side="left")
    
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill="x", pady=10)
    
    ttk.Button(btn_frame, text="+ Tambah Tugas", command=app._add_bab2).pack(side="left", padx=2)
    ttk.Button(btn_frame, text="✏️ Edit", command=app._edit_bab2).pack(side="left", padx=2)
    ttk.Button(btn_frame, text="🗑️ Hapus", command=app._remove_bab2).pack(side="left", padx=2)

    # Listbox dengan Border & Scrollbar
    list_container = ttk.Frame(frame)
    list_container.pack(fill="both", expand=True)
    
    app.bab2_listbox = tk.Listbox(
        list_container, 
        font=("Segoe UI", 11), 
        borderwidth=1, 
        relief="flat",
        selectbackground="#007bff",
        highlightthickness=0,
        activestyle='none'
    )
    app.bab2_listbox.pack(side="left", fill="both", expand=True)
    
    scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=app.bab2_listbox.yview)
    scrollbar.pack(side="right", fill="y")
    app.bab2_listbox.config(yscrollcommand=scrollbar.set)