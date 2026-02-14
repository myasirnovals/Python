import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class Bab3Tab(ttk.Frame):
    def __init__(self, app, parent):
        super().__init__(parent, padding=20)
        self.app = app
        self.kesimpulan_text = None
        self._build()

    def _build(self):
        self.pack(fill="both", expand=True)

        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(
            header_frame, 
            text="Kesimpulan Laporan", 
            style="Header.TLabel"
        ).pack(side="left")

        # Toolbar untuk AI
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 10))
        
        ttk.Button(
            toolbar, 
            text="✨ Generate Kesimpulan (AI)", 
            style="Action.TButton",
            command=self._run_kesimpulan_ai
        ).pack(side="left")

        ttk.Label(
            self, 
            text="Anda dapat mengedit kesimpulan secara manual di bawah ini:",
            foreground="#666666"
        ).pack(anchor="w", pady=(5, 5))

        # Area Teks Kesimpulan
        self.kesimpulan_text = scrolledtext.ScrolledText(
            self, 
            wrap="word", 
            height=16,
            font=("Segoe UI", 11),
            padx=10,
            pady=10
        )
        self.kesimpulan_text.pack(fill="both", expand=True)

    def _run_kesimpulan_ai(self):
        # 1. Ambil data dari Bab 1 dan Bab 2 melalui referensi app
        data_bab1 = self.app.bab1_tab.get_items()
        data_bab2 = self.app.bab2_tab.get_items()

        # Validasi jika data masih kosong
        if not data_bab1 and not data_bab2:
            messagebox.showwarning(
                "Data Kosong", 
                "Daftar Hasil Praktikum (Bab 1) atau Tugas (Bab 2) belum diisi. AI membutuhkan data tersebut untuk membuat kesimpulan."
            )
            return

        # 2. Panggil service backend (Logika UI saja)
        # Catatan: Prompt internal untuk AI akan meminta 3 paragraf (5-10 kalimat per paragraf)
        # berdasarkan data_bab1 dan data_bab2 yang dikirimkan.
        res, err = self.app.analysis_service.generate_conclusion(
            data_bab1, 
            data_bab2
        )

        if err:
            messagebox.showerror("AI Error", err)
            return

        # 3. Update UI dengan hasil dari AI
        self.kesimpulan_text.delete("1.0", tk.END)
        self.kesimpulan_text.insert("1.0", res)

    def get_kesimpulan(self):
        """Method untuk mengambil teks akhir untuk proses render report"""
        if not self.kesimpulan_text:
            return ""
        return self.kesimpulan_text.get("1.0", "end-1c")