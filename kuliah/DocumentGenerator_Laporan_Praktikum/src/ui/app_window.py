import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext

from app.ai_client import GeminiClient
from app.services.analysis_service import AnalysisService
from app.services.report_service import ReportService
from ui.bab1_tab import build_bab1_tab
from ui.bab2_tab import build_bab2_tab
from ui.bab3_tab import build_bab3_tab
from ui.cover_tab import build_cover_tab
from ui.generate_tab import build_generate_tab

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "templates")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lab Report Generator Pro")
        self.geometry("1080x800")
        
        # 1. Inisialisasi Style Sebelum Build UI
        self._setup_styles()

        self.ai_client = GeminiClient()
        self.analysis_service = AnalysisService(self.ai_client)
        self.report_service = ReportService(TEMPLATES_DIR)

        self.cover_vars = {
            "mata_kuliah": tk.StringVar(),
            "nomor_modul": tk.StringVar(),
            "judul": tk.StringVar(),
            "nama": tk.StringVar(),
            "nim": tk.StringVar(),
            "tahun": tk.StringVar(),
        }
        self.template_choice = tk.StringVar(value="1")
        self.bab1_items = []
        self.bab2_items = []
        self.kesimpulan_text = None

        self._build_ui()

    def _setup_styles(self):
        """Konfigurasi tema dan gaya visual aplikasi"""
        style = ttk.Style(self)
        style.theme_use('clam') # 'clam' lebih mudah di-custom warnanya
        
        # Palet Warna & Font
        bg_main = "#f8f9fa"
        accent_blue = "#007bff"
        text_dark = "#212529"
        
        style.configure("TFrame", background=bg_main)
        style.configure("TLabel", background=bg_main, foreground=text_dark, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground=accent_blue)
        style.configure("Subheader.TLabel", font=("Segoe UI", 11, "bold"))
        
        # Styling Notebook (Tabs)
        style.configure("TNotebook", background=bg_main, borderwidth=0)
        style.configure("TNotebook.Tab", padding=[20, 10], font=("Segoe UI", 10))
        style.map("TNotebook.Tab", 
                  background=[("selected", accent_blue)], 
                  foreground=[("selected", "white")])

        # Styling Buttons
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), foreground="white", background=accent_blue)
        style.map("Action.TButton", background=[('active', '#0056b3')])
        
        # Styling Entry & Labelframe
        style.configure("TLabelframe", background=bg_main, relief="groove")
        style.configure("TLabelframe.Label", background=bg_main, font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        self.configure(bg="#f8f9fa")
        
        # Container Utama
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=25, pady=25)

        # Header Aplikasi
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill="x", pady=(0, 20))
        ttk.Label(header_frame, text="Lab Report Generator", style="Header.TLabel").pack(side="left")
        ttk.Label(header_frame, text="v2.0 Beta", foreground="#6c757d").pack(side="left", padx=10, pady=(5,0))

        # Notebook Area
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)

        tabs = [
            ("Cover", build_cover_tab),
            ("Langkah Kerja", build_bab1_tab),
            ("Tugas & Jawaban", build_bab2_tab),
            ("Kesimpulan", build_bab3_tab),
            ("Selesai", build_generate_tab)
        ]

        for text, builder in tabs:
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=text)
            builder(self, tab_frame)

    # --- Refactored Dialogs ---

    def _open_bab1_dialog(self, initial=None):
        """Dialog untuk Bab 1 yang dipercantik dengan tata letak yang lebih lega"""
        dialog = tk.Toplevel(self)
        dialog.title("Editor Langkah Kerja")
        dialog.geometry("900x800")
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self)
        dialog.grab_set()

        data = initial.copy() if initial else {}
        tipe_var = tk.StringVar(value=data.get("tipe", "1"))
        judul_var = tk.StringVar(value=data.get("judul_sub_bab", ""))

        container = ttk.Frame(dialog, padding=20)
        container.pack(fill="both", expand=True)

        # Bagian Atas: Info Dasar
        info_frame = ttk.LabelFrame(container, text=" Informasi Dasar ", padding=15)
        info_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(info_frame, text="Judul Sub-Bab:").grid(row=0, column=0, sticky="w")
        ttk.Entry(info_frame, textvariable=judul_var, width=70).grid(row=0, column=1, padx=10, sticky="ew")
        
        type_choice_frame = ttk.Frame(info_frame)
        type_choice_frame.grid(row=1, column=1, sticky="w", pady=(10, 0))
        ttk.Label(info_frame, text="Tipe Konten:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Radiobutton(type_choice_frame, text="Source Code", variable=tipe_var, value="1").pack(side="left")
        ttk.Radiobutton(type_choice_frame, text="Langkah Deskriptif", variable=tipe_var, value="2").pack(side="left", padx=20)

        # Bagian Tengah: Editor Konten
        content_frame = ttk.LabelFrame(container, text=" Isi & Dokumentasi ", padding=15)
        content_frame.pack(fill="both", expand=True)

        # 1. Area Teks (untuk Langkah Kerja)
        self.isi_a_text = scrolledtext.ScrolledText(content_frame, height=8, font=("Segoe UI", 10))
        if data.get("isi_a"): self.isi_a_text.insert("1.0", data.get("isi_a"))

        # 2. Area Kode
        self.kode_items = data.get("kode_files", [])
        self.kode_container = ttk.Frame(content_frame)
        self.kode_listbox = tk.Listbox(self.kode_container, height=6, font=("Consolas", 10))
        self.kode_listbox.pack(side="left", fill="both", expand=True)
        
        k_btns = ttk.Frame(self.kode_container)
        k_btns.pack(side="right", padx=(10, 0))
        ttk.Button(k_btns, text="Add Code", command=self._add_kode_logic).pack(fill="x", pady=2)
        ttk.Button(k_btns, text="Remove", command=self._remove_kode_logic).pack(fill="x")

        # 3. Area Gambar (Selalu Muncul)
        img_label = ttk.Label(content_frame, text="Lampiran Gambar:", style="Subheader.TLabel")
        img_label.pack(anchor="w", pady=(15, 5))
        
        self.gambar_items = data.get("gambar_paths", [])
        img_main = ttk.Frame(content_frame)
        img_main.pack(fill="x")
        
        self.gambar_listbox = tk.Listbox(img_main, height=4, font=("Segoe UI", 9))
        self.gambar_listbox.pack(side="left", fill="both", expand=True)
        
        g_btns = ttk.Frame(img_main)
        g_btns.pack(side="right", padx=(10, 0))
        ttk.Button(g_btns, text="+ Gambar", command=self._add_gambar_logic).pack(fill="x", pady=2)
        ttk.Button(g_btns, text="Hapus", command=self._remove_gambar_logic).pack(fill="x")

        # Bagian Bawah: Analisa AI
        ai_frame = ttk.LabelFrame(container, text=" Analisa Hasil (AI) ", padding=15)
        ai_frame.pack(fill="both", expand=True, pady=(15, 0))
        
        analisa_text = scrolledtext.ScrolledText(ai_frame, height=6, font=("Segoe UI", 10), bg="#fcfcfc")
        analisa_text.pack(fill="both", expand=True)
        if data.get("analisa"): analisa_text.insert("1.0", data.get("analisa"))

        def run_ai():
            res, err = self.analysis_service.generate_analysis(
                tipe_var.get(), self.isi_a_text.get("1.0", tk.END), 
                self.kode_items, self.gambar_items, self.template_choice.get()
            )
            if err: messagebox.showerror("AI Error", err)
            else:
                analisa_text.delete("1.0", tk.END)
                analisa_text.insert("1.0", res)

        ttk.Button(ai_frame, text="✨ Generate Analisa Otomatis", style="Action.TButton", command=run_ai).pack(pady=10)

        # Logic Visibility
        def toggle_view(*args):
            if tipe_var.get() == "1":
                self.isi_a_text.pack_forget()
                self.kode_container.pack(fill="both", expand=True)
            else:
                self.kode_container.pack_forget()
                self.isi_a_text.pack(fill="both", expand=True)

        tipe_var.trace_add("write", toggle_view)
        toggle_view()
        self._refresh_dialog_lists()

        # Final Actions
        res_val = {"data": None}
        def save():
            res_val["data"] = {
                "judul_sub_bab": judul_var.get(),
                "tipe": tipe_var.get(),
                "isi_a": self.isi_a_text.get("1.0", "end-1c"),
                "kode_files": self.kode_items,
                "gambar_paths": self.gambar_items,
                "analisa": analisa_text.get("1.0", "end-1c")
            }
            dialog.destroy()

        btn_row = ttk.Frame(container)
        btn_row.pack(fill="x", pady=(20, 0))
        ttk.Button(btn_row, text="Simpan Ke Laporan", style="Action.TButton", command=save).pack(side="right", padx=5)
        ttk.Button(btn_row, text="Batal", command=dialog.destroy).pack(side="right")

        self.wait_window(dialog)
        return res_val["data"]

    # --- Helper Logic untuk Dialog ---

    def _refresh_dialog_lists(self):
        if hasattr(self, 'kode_listbox'):
            self.kode_listbox.delete(0, tk.END)
            for f in self.kode_items: self.kode_listbox.insert(tk.END, f"📄 {f['nama']}")
        
        if hasattr(self, 'gambar_listbox'):
            self.gambar_listbox.delete(0, tk.END)
            for g in self.gambar_items: 
                self.gambar_listbox.insert(tk.END, f"🖼️ {os.path.basename(g['path'])} ({g['caption']})")

    def _add_kode_logic(self):
        res = self._open_kode_dialog()
        if res:
            self.kode_items.append(res)
            self._refresh_dialog_lists()

    def _remove_kode_logic(self):
        sel = self.kode_listbox.curselection()
        if sel:
            self.kode_items.pop(sel[0])
            self._refresh_dialog_lists()

    def _add_gambar_logic(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if path:
            cap = self._prompt_caption()
            if cap is not None:
                self.gambar_items.append({"path": path, "caption": cap})
                self._refresh_dialog_lists()

    def _remove_gambar_logic(self):
        sel = self.gambar_listbox.curselection()
        if sel:
            self.gambar_items.pop(sel[0])
            self._refresh_dialog_lists()

    # --- Sisa Fungsi (Refresh List Tab & Generate) tetap dipertahankan ---
    def _refresh_bab1_list(self):
        self.bab1_listbox.delete(0, tk.END)
        for i, item in enumerate(self.bab1_items, 1):
            judul = item.get("judul_sub_bab") or f"Sub-Bab {i}"
            tipe = "Source Code" if item.get("tipe") == "1" else "Langkah Kerja"
            self.bab1_listbox.insert(tk.END, f" {i}. {judul.upper()} — [{tipe}]")

    def _refresh_bab2_list(self):
        self.bab2_listbox.delete(0, tk.END)
        for i, item in enumerate(self.bab2_items, 1):
            judul = item.get("judul_sub_bab") or f"Tugas {i}"
            self.bab2_listbox.insert(tk.END, f"{i}. {judul}")

    def _add_bab1(self):
        data = self._open_bab1_dialog()
        if data:
            self.bab1_items.append(data)
            self._refresh_bab1_list()

    def _edit_bab1(self):
        sel = self.bab1_listbox.curselection()
        if not sel:
            return
        index = sel[0]
        data = self._open_bab1_dialog(self.bab1_items[index])
        if data:
            self.bab1_items[index] = data
            self._refresh_bab1_list()

    def _remove_bab1(self):
        sel = self.bab1_listbox.curselection()
        if not sel:
            return
        index = sel[0]
        del self.bab1_items[index]
        self._refresh_bab1_list()

    def _add_bab2(self):
        data = self._open_bab2_dialog()
        if data:
            self.bab2_items.append(data)
            self._refresh_bab2_list()

    def _edit_bab2(self):
        sel = self.bab2_listbox.curselection()
        if not sel:
            return
        index = sel[0]
        data = self._open_bab2_dialog(self.bab2_items[index])
        if data:
            self.bab2_items[index] = data
            self._refresh_bab2_list()

    def _remove_bab2(self):
        sel = self.bab2_listbox.curselection()
        if not sel:
            return
        index = sel[0]
        del self.bab2_items[index]
        self._refresh_bab2_list()

    def _open_bab2_dialog(self, initial=None):
        dialog = tk.Toplevel(self)
        dialog.title("Tugas Praktikum")
        dialog.geometry("760x640")
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self)
        dialog.grab_set()

        data = initial.copy() if initial else {}

        judul_var = tk.StringVar(value=data.get("judul_sub_bab", ""))
        ttk.Label(dialog, text="Topik Tugas").pack(anchor="w", padx=12, pady=6)
        ttk.Entry(dialog, textvariable=judul_var, width=60).pack(anchor="w", padx=12)

        ttk.Label(dialog, text="Soal").pack(anchor="w", padx=12, pady=6)
        soal_text = scrolledtext.ScrolledText(dialog, height=6, wrap="word")
        soal_text.pack(fill="both", expand=False, padx=12)
        if data.get("isi_soal"):
            soal_text.insert("1.0", data.get("isi_soal"))

        ttk.Label(dialog, text="Jawaban").pack(anchor="w", padx=12, pady=6)
        jawab_text = scrolledtext.ScrolledText(dialog, height=6, wrap="word")
        jawab_text.pack(fill="both", expand=False, padx=12)
        if data.get("isi_jawaban"):
            jawab_text.insert("1.0", data.get("isi_jawaban"))

        gambar_frame = ttk.LabelFrame(dialog, text="Gambar")
        gambar_frame.pack(fill="both", expand=False, padx=12, pady=8)
        gambar_list = tk.Listbox(gambar_frame, height=5)
        gambar_list.pack(fill="both", expand=True, padx=6, pady=6)
        gambar_items = data.get("gambar_paths", [])

        def refresh_gambar_list():
            gambar_list.delete(0, tk.END)
            for i, item in enumerate(gambar_items, 1):
                name = os.path.basename(item.get("path", ""))
                caption = item.get("caption", "")
                gambar_list.insert(tk.END, f"{i}. {name} - {caption}")

        def add_gambar():
            path = filedialog.askopenfilename(
                title="Pilih Gambar",
                filetypes=[("Image", "*.png;*.jpg;*.jpeg;*.bmp")],
            )
            if not path:
                return
            caption = self._prompt_caption()
            if caption is None:
                return
            gambar_items.append({"path": path, "caption": caption})
            refresh_gambar_list()

        def remove_gambar():
            sel = gambar_list.curselection()
            if not sel:
                return
            idx = sel[0]
            del gambar_items[idx]
            refresh_gambar_list()

        toolbar = ttk.Frame(gambar_frame)
        toolbar.pack(fill="x", padx=6, pady=4)
        ttk.Button(toolbar, text="Tambah Gambar", command=add_gambar).pack(
            side="left"
        )
        ttk.Button(toolbar, text="Hapus", command=remove_gambar).pack(
            side="left", padx=6
        )

        refresh_gambar_list()

        result = {"value": None}

        def on_save():
            judul = judul_var.get().strip()
            if not judul:
                messagebox.showwarning("Validasi", "Topik tugas belum diisi.")
                return

            soal = soal_text.get("1.0", "end-1c").strip()
            jawab = jawab_text.get("1.0", "end-1c").strip()
            if not soal or not jawab:
                messagebox.showwarning("Validasi", "Soal dan jawaban wajib diisi.")
                return

            result["value"] = {
                "judul_sub_bab": judul,
                "isi_soal": soal_text.get("1.0", "end-1c"),
                "isi_jawaban": jawab_text.get("1.0", "end-1c"),
                "gambar_paths": gambar_items,
            }
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        action_frame = ttk.Frame(dialog)
        action_frame.pack(fill="x", padx=12, pady=10)
        ttk.Button(action_frame, text="Simpan", command=on_save).pack(
            side="right", padx=6
        )
        ttk.Button(action_frame, text="Batal", command=on_cancel).pack(side="right")

        self.wait_window(dialog)
        return result["value"]

    def _open_kode_dialog(self, initial=None):
        dialog = tk.Toplevel(self)
        dialog.title("File Kode")
        dialog.geometry("640x520")
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self)
        dialog.grab_set()

        nama_var = tk.StringVar(value=(initial or {}).get("nama", ""))
        ttk.Label(dialog, text="Nama File").pack(anchor="w", padx=12, pady=6)
        ttk.Entry(dialog, textvariable=nama_var, width=50).pack(anchor="w", padx=12)

        ttk.Label(dialog, text="Isi Kode").pack(anchor="w", padx=12, pady=6)
        isi_text = scrolledtext.ScrolledText(dialog, height=16, wrap="none")
        isi_text.pack(fill="both", expand=True, padx=12)
        if initial and initial.get("isi"):
            isi_text.insert("1.0", initial.get("isi"))

        result = {"value": None}

        def on_save():
            nama = nama_var.get().strip()
            isi = isi_text.get("1.0", "end-1c")
            if not isi.strip():
                messagebox.showwarning("Validasi", "Isi kode tidak boleh kosong.")
                return
            result["value"] = {"nama": nama, "isi": isi}
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        action_frame = ttk.Frame(dialog)
        action_frame.pack(fill="x", padx=12, pady=10)
        ttk.Button(action_frame, text="Simpan", command=on_save).pack(
            side="right", padx=6
        )
        ttk.Button(action_frame, text="Batal", command=on_cancel).pack(side="right")

        self.wait_window(dialog)
        return result["value"]

    def _prompt_caption(self):
        dialog = tk.Toplevel(self)
        dialog.title("Caption")
        dialog.geometry("420x160")
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self)
        dialog.grab_set()

        caption_var = tk.StringVar()
        ttk.Label(dialog, text="Caption").pack(anchor="w", padx=12, pady=8)
        ttk.Entry(dialog, textvariable=caption_var, width=48).pack(anchor="w", padx=12)

        result = {"value": None}

        def on_save():
            result["value"] = caption_var.get()
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        action_frame = ttk.Frame(dialog)
        action_frame.pack(fill="x", padx=12, pady=10)
        ttk.Button(action_frame, text="OK", command=on_save).pack(
            side="right", padx=6
        )
        ttk.Button(action_frame, text="Batal", command=on_cancel).pack(side="right")

        self.wait_window(dialog)
        return result["value"]

    def _generate(self):
        cover = {}
        for key, var in self.cover_vars.items():
            cover[key] = var.get().strip()

        required = ["mata_kuliah", "nomor_modul", "judul", "nama", "nim", "tahun"]
        if any(not cover[k] for k in required):
            messagebox.showwarning("Validasi", "Data cover belum lengkap.")
            return

        cover["mata_kuliah"] = cover["mata_kuliah"].upper()
        cover["judul"] = cover["judul"].upper()
        cover["nama"] = cover["nama"].upper()

        kesimpulan = (
            self.kesimpulan_text.get("1.0", "end-1c") if self.kesimpulan_text else ""
        )
        if not kesimpulan.strip():
            messagebox.showwarning("Validasi", "Kesimpulan belum diisi.")
            return

        output_name = (
            f"Laporan_Modul_{cover['nomor_modul']}_{cover['nama'].replace(' ', '_')}.docx"
        )
        output_path = filedialog.asksaveasfilename(
            title="Simpan Laporan",
            defaultextension=".docx",
            initialfile=output_name,
            filetypes=[("Word Document", "*.docx")],
        )
        if not output_path:
            return

        try:
            self.report_service.render_report(
                self.template_choice.get(),
                cover,
                self.bab1_items,
                self.bab2_items,
                kesimpulan,
                output_path,
            )
            messagebox.showinfo("Sukses", f"Laporan tersimpan di:\n{output_path}")
        except FileNotFoundError as e:
            messagebox.showerror(
                "Template Tidak Ada",
                f"File template '{e.args[0]}' tidak ditemukan.",
            )
        except Exception as e:
            messagebox.showerror("Gagal", f"Gagal render: {e}")