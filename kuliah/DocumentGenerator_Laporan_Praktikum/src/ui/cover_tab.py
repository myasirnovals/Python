import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

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
        self.api_key_var = tk.StringVar()
        self.api_key_status_var = tk.StringVar(value="Belum diinput")
        self.modul_path_var = tk.StringVar()
        self.modul_text_cache = ""
        self.modul_loaded_path = ""
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

        # --- GROUP 3: PENGATURAN DOKUMEN ---
        group3 = ttk.LabelFrame(self, text=" Pengaturan Dokumen ", padding=20)
        group3.pack(fill="x", pady=(0, 5)) 
        group3.columnconfigure(1, weight=1)
        group3.columnconfigure(2, weight=1)
        group3.rowconfigure(0, weight=1) 

        # 1. Pilih Gaya Laporan
        ttk.Label(group3, text="Pilih Gaya Laporan:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Radiobutton(group3, text="Nur Faid Prasetyo", variable=self.template_choice, value="1").grid(row=0, column=1, sticky="w", padx=5)
        ttk.Radiobutton(group3, text="Astriani Komeri", variable=self.template_choice, value="2").grid(row=0, column=2, sticky="w", padx=5)
        ttk.Radiobutton(group3, text="Sri Akmaliatul Maulani", variable=self.template_choice, value="3").grid(row=0, column=3, sticky="w", padx=5)

        ttk.Separator(group3, orient="horizontal").grid(row=1, column=0, columnspan=4, sticky="ew", pady=(12, 12))

        # 2. File Modul (Naik ke atas API KEY)
        modul_row = ttk.Frame(group3)
        modul_row.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(0, 10))
        modul_row.columnconfigure(1, weight=1)

        ttk.Label(modul_row, text="File Modul:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Label(modul_row, textvariable=self.modul_path_var, foreground="#6c757d").grid(row=0, column=1, sticky="ew")
        ttk.Button(modul_row, text="Input File Modul", style="Action.TButton", command=self._open_modul_input_popup).grid(row=0, column=2, sticky="e", padx=(10, 0))

        # 3. API KEY (Sekarang di paling bawah)
        api_row = ttk.Frame(group3)
        api_row.grid(row=3, column=0, columnspan=4, sticky="ew")
        api_row.columnconfigure(1, weight=1)

        ttk.Label(api_row, text="API KEY:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # Field dibuat statis (12 bintang), tidak bisa diedit, dan mematikan fungsi copy/paste
        self.api_display_var = tk.StringVar(value="************") 
        ttk.Label(api_row, textvariable=self.api_display_var, foreground="#6c757d").grid(row=0, column=1, sticky="ew")

        ttk.Button(api_row, text="AI KEY", style="Action.TButton", command=self._input_api_key).grid(row=0, column=3, sticky="e", padx=(10, 0))

        # Memastikan API Key kosong saat aplikasi dijalankan (Keamanan)
        self._force_secure_clear()

    def _force_secure_clear(self):
        """Memaksa semua variabel API Key kosong saat startup demi keamanan"""
        os.environ["AI_API_KEY"] = ""
        os.environ["GEMINI_API_KEY"] = ""
        self.app.ai_client.api_key = ""
        self.api_key_var.set("")
        # Tampilan tetap bintang tapi variabel asli kosong
        self.api_key_status_var.set("")

    def get_cover_data(self):
        return {key: var.get().strip() for key, var in self.cover_vars.items()}

    def get_template_choice(self):
        return self.template_choice.get()

    def get_modul_text(self):
        return self.modul_text_cache

    def get_modul_path(self):
        return self.modul_loaded_path

    def _refresh_api_key_state(self):
        current_key = (self.app.ai_client.api_key or "").strip()
        self.api_key_var.set(current_key)
        self.api_key_status_var.set("Sudah diinput" if current_key else "Belum diinput")

    def _input_api_key(self):
        api_key = simpledialog.askstring(
            "AI API Key",
            "Masukkan AI_API_KEY (Gemini API Key):",
            parent=self,
            show="*",
        )

        if api_key is None:
            return

        cleaned_key = api_key.strip()
        if not cleaned_key:
            messagebox.showwarning("Input Kosong", "AI_API_KEY tidak boleh kosong.")
            return

        os.environ["AI_API_KEY"] = cleaned_key
        os.environ["GEMINI_API_KEY"] = cleaned_key
        self.app.ai_client.api_key = cleaned_key
        self.app.ai_client.model_name = None
        self._refresh_api_key_state()

        messagebox.showinfo("Berhasil", "AI_API_KEY berhasil diperbarui untuk sesi ini.")

    def _open_modul_input_popup(self):
        dialog = tk.Toplevel(self)
        dialog.title("Input File Modul")
        dialog.geometry("560x180")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        selected_path = tk.StringVar(value=self.modul_loaded_path)

        wrapper = ttk.Frame(dialog, padding=16)
        wrapper.pack(fill="both", expand=True)
        wrapper.columnconfigure(0, weight=1)

        ttk.Label(
            wrapper,
            text="Pilih file modul (hanya PDF atau DOC)",
        ).pack(anchor="w", pady=(0, 8))

        path_row = ttk.Frame(wrapper)
        path_row.pack(fill="x")
        path_row.columnconfigure(0, weight=1)

        ttk.Entry(path_row, textvariable=selected_path, state="readonly").grid(
            row=0, column=0, sticky="ew"
        )

        def browse_file():
            path = filedialog.askopenfilename(
                title="Pilih File Modul",
                filetypes=[("Dokumen", "*.pdf;*.doc"), ("PDF", "*.pdf"), ("DOC", "*.doc")],
            )
            if path:
                selected_path.set(path)

        ttk.Button(path_row, text="...", width=3, command=browse_file).grid(
            row=0, column=1, padx=(6, 0)
        )

        btn_row = ttk.Frame(wrapper)
        btn_row.pack(fill="x", pady=(14, 0))

        def save_modul():
            path = selected_path.get().strip()
            if not path:
                messagebox.showwarning("Validasi", "File modul belum dipilih.")
                return

            ext = path.lower().split(".")[-1]
            if ext not in {"pdf", "doc"}:
                messagebox.showwarning("Validasi", "Format tidak valid. Hanya file PDF atau DOC yang diizinkan.")
                return

            text = self.app.analysis_service.read_modul_text(path)
            if not text:
                messagebox.showwarning("Modul", "Modul kosong atau gagal dibaca.")
                return

            self.modul_text_cache = text
            self.modul_loaded_path = path
            self.modul_path_var.set(path)
            messagebox.showinfo("Modul", f"Modul berhasil dimuat ({len(text)} karakter).")
            dialog.destroy()

        ttk.Button(btn_row, text="Simpan", style="Action.TButton", command=save_modul).pack(side="right", padx=(6, 0))
        ttk.Button(btn_row, text="Batal", command=dialog.destroy).pack(side="right")

        self.wait_window(dialog)

    def fill_test_data(self):
        self.cover_vars["mata_kuliah"].set("Pemrograman Dasar")
        self.cover_vars["nomor_modul"].set("03")
        self.cover_vars["judul"].set("Percabangan dan Perulangan")
        self.cover_vars["nama"].set("Budi Santoso")
        self.cover_vars["nim"].set("2201234567")
        self.cover_vars["tahun"].set("2025/2026")
        self.template_choice.set("1")