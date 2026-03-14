import os
import re
import tempfile
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext
from tkinterdnd2 import DND_FILES, TkinterDnD

from PIL import ImageGrab


class Bab1Tab(ttk.Frame):
    def __init__(self, app, parent):
        super().__init__(parent, padding=20)
        self.app = app
        self.bab1_items = []
        self._active_bab1_dialog = None

        self.isi_a_text = None
        self.kode_items = []
        self.kode_container = None
        self.kode_listbox = None
        self.gambar_items = []
        self.gambar_listbox = None

        self._build()

    def _build(self):
        self.pack(fill="both", expand=True)

        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(
            header_frame,
            text="Daftar Hasil Praktikum",
            style="Header.TLabel",
        ).pack(side="left")

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="+ Tambah Sub-Bab", command=self._add_bab1).pack(
            side="left", padx=2
        )
        ttk.Button(btn_frame, text="✏️ Edit", command=self._edit_bab1).pack(
            side="left", padx=2
        )
        ttk.Button(btn_frame, text="🗑️ Hapus", command=self._remove_bab1).pack(
            side="left", padx=2
        )

        list_container = ttk.Frame(self)
        list_container.pack(fill="both", expand=True)

        self.bab1_listbox = tk.Listbox(
            list_container,
            font=("Segoe UI", 11),
            borderwidth=1,
            relief="flat",
            selectbackground="#007bff",
            highlightthickness=0,
            activestyle="none",
        )
        self.bab1_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            list_container, orient="vertical", command=self.bab1_listbox.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.bab1_listbox.config(yscrollcommand=scrollbar.set)

    def get_items(self):
        return self.bab1_items

    def fill_test_data(self):
        self.bab1_items = [
            {
                "judul_sub_bab": "Percobaan 1: Percabangan",
                "tipe": "2",
                "isi_a": "Jika nilai lebih besar dari 75 maka tampilkan LULUS.",
                "kode_files": [],
                "gambar_paths": [],
                "analisa": "Program memeriksa kondisi nilai dan menampilkan status sesuai aturan.",
            }
        ]
        self._refresh_bab1_list()

    def _refresh_bab1_list(self):
        self.bab1_listbox.delete(0, tk.END)
        for i, item in enumerate(self.bab1_items, 1):
            judul = item.get("judul_sub_bab") or f"Sub-Bab {i}"
            tipe = "Source Code" if item.get("tipe") == "1" else "Langkah Kerja"
            self.bab1_listbox.insert(tk.END, f" {i}. {judul.upper()} — [{tipe}]")

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

    def _open_bab1_dialog(self, initial=None):
        dialog = tk.Toplevel(self)
        self._active_bab1_dialog = dialog
        dialog.title("Editor Hasil Praktikum")
        
        # IMK: Ukuran ideal untuk layar laptop menengah (950x600)
        dialog.geometry("980x600")
        dialog.minsize(860, 540)
        dialog.resizable(True, True)
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self)
        dialog.grab_set()

        # Logika Bisnis: Data Awal
        data = initial.copy() if initial else {}
        tipe_var = tk.StringVar(value=data.get("tipe") or data.get("tipe_konten", "1"))
        judul_var = tk.StringVar(value=data.get("judul_sub_bab") or data.get("judul_tugas", ""))
        self.kode_items = data.get("list_kode") or data.get("kode_files", [])
        self.gambar_items = data.get("list_gambar") or data.get("gambar_paths", [])

        initial_penjelasan = data.get("penjelasan_singkat", "")
        initial_isi_a = data.get("isi_a", "")
        if not initial_isi_a:
            raw_langkah = data.get("langkah_list") or data.get("langkah_kerja_items")
            if isinstance(raw_langkah, list):
                rows = []
                for idx, item in enumerate(raw_langkah, 1):
                    if isinstance(item, dict):
                        nomor = item.get("nomor", idx)
                        teks = item.get("langkah_kerja", "").strip()
                    else:
                        nomor = idx
                        teks = str(item).strip()
                    if teks:
                        rows.append(f"{nomor}. {teks}")
                initial_isi_a = "\n".join(rows)
            elif isinstance(raw_langkah, str):
                initial_isi_a = raw_langkah

        initial_analisa = data.get("isi_analisa") or data.get("analisa", "")

        # --- FOOTER NAVIGATION (Statis di bawah) ---
        btn_row = ttk.Frame(dialog, padding=(20, 10))
        btn_row.pack(side="bottom", fill="x")
        ttk.Separator(dialog, orient="horizontal").pack(side="bottom", fill="x")

        res_val = {"data": None}

        def save():
            raw_text = self.isi_a_text.get("1.0", "end-1c")
    
            langkah_list = []
            # Memecah baris dan membersihkan karakter whitespace standar
            lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
            
            for i, line in enumerate(lines, 1):
                # 1. Membersihkan karakter aneh/non-printable di awal string (BOM, dsb)
                # re.sub(r'^[^\w\s]+', '', line) akan menghapus simbol aneh di depan
                clean_line = re.sub(r'^[^\w\s\d]+', '', line).strip()

                # 2. Regex yang lebih toleran: 
                # ^\s*(\d+)   : Mencari angka di awal
                # [\s\.\)\-]* : Mencari pemisah (titik, kurung, strip, spasi)
                # (.*)        : Mengambil sisa kalimatnya
                match = re.match(r'^\s*(\d+)[\s\.\)\-]*\s*(.*)', clean_line)
                
                if match:
                    nomor_ditemukan = match.group(1)
                    teks_asli = match.group(2).strip()
                    
                    langkah_list.append({
                        "nomor": nomor_ditemukan, 
                        "langkah_kerja": teks_asli
                    })
                else:
                    # Jika tidak ada pola angka, gunakan index loop
                    langkah_list.append({
                        "nomor": i, 
                        "langkah_kerja": clean_line
                    })
            
            label_a = "Source Code" if tipe_var.get() == "1" else "Langkah Kerja"

            res_val["data"] = {
                "judul_sub_bab": judul_var.get(),
                "penjelasan_singkat": penjelasan_text.get("1.0", "end-1c"),
                "tipe": tipe_var.get(),
                "label_point_a": label_a,
                "list_kode": self.kode_items,
                "langkah_list": langkah_list,
                "list_gambar": self.gambar_items,
                "isi_analisa": analisa_text.get("1.0", "end-1c"),
            }
            dialog.destroy()

        ttk.Button(btn_row, text="Simpan Ke Laporan", style="Action.TButton", command=save).pack(side="right", padx=5)
        ttk.Button(btn_row, text="Batal", command=dialog.destroy).pack(side="right")

        # --- BODY SPLIT VIEW (Scroll + Responsive) ---
        body_host = ttk.Frame(dialog)
        body_host.pack(fill="both", expand=True)

        body_canvas = tk.Canvas(body_host, highlightthickness=0, bg="#f8f9fa")
        body_scrollbar = ttk.Scrollbar(body_host, orient="vertical", command=body_canvas.yview)
        body_canvas.configure(yscrollcommand=body_scrollbar.set)

        body_scrollbar.pack(side="right", fill="y")
        body_canvas.pack(side="left", fill="both", expand=True)

        scrollable_body = ttk.Frame(body_canvas, padding=15)
        body_window = body_canvas.create_window((0, 0), window=scrollable_body, anchor="nw")

        scrollable_body.bind(
            "<Configure>",
            lambda e: body_canvas.configure(scrollregion=body_canvas.bbox("all")),
        )
        body_canvas.bind(
            "<Configure>",
            lambda e: body_canvas.itemconfigure(body_window, width=e.width),
        )

        def _on_mousewheel(event):
            body_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        body_canvas.bind("<Enter>", lambda e: body_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        body_canvas.bind("<Leave>", lambda e: body_canvas.unbind_all("<MouseWheel>"))

        main_container = ttk.Frame(scrollable_body)
        main_container.pack(fill="both", expand=True)

        content_split = ttk.Frame(main_container)
        content_split.pack(fill="both", expand=True)

        # Bagian Kiri: Input & Dokumentasi
        left_pane = ttk.Frame(content_split)
        left_pane.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Bagian Kanan: Analisa AI
        right_pane = ttk.Frame(content_split)
        right_pane.pack(side="right", fill="both", expand=True)

        # --- LEFT PANE CONTENT ---
        # 1. Informasi Dasar (Compact)
        info_frame = ttk.LabelFrame(left_pane, text=" Informasi Dasar ", padding=10)
        info_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(info_frame, text="Judul Sub-Bab:").pack(anchor="w")
        ttk.Entry(info_frame, textvariable=judul_var).pack(fill="x", pady=(2, 5))
        
        ttk.Label(info_frame, text="Penjelasan Singkat:").pack(anchor="w")
        penjelasan_text = tk.Text(info_frame, height=3, font=("Segoe UI", 10), relief="solid", borderwidth=1)
        penjelasan_text.pack(fill="x", pady=(2, 5))
        if initial_penjelasan:
            penjelasan_text.insert("1.0", initial_penjelasan)

        action_row = ttk.Frame(info_frame)
        action_row.pack(fill="x", pady=5)
        
        # Sisi Kiri: Tipe Konten
        type_row = ttk.Frame(action_row)
        type_row.pack(side="left")
        ttk.Label(type_row, text="Tipe Konten:").pack(side="left")
        ttk.Radiobutton(type_row, text="Source Code", variable=tipe_var, value="1").pack(side="left", padx=10)
        ttk.Radiobutton(type_row, text="Langkah Kerja", variable=tipe_var, value="2").pack(side="left")
        
        # Sisi Kanan: Tombol Penjelasan AI
        def run_penjelasan_ai():
            judul = judul_var.get().strip()
            if not judul:
                messagebox.showwarning("Validasi", "Isi Judul Sub-Bab terlebih dahulu agar AI memahami konteks.")
                return

            modul_text = self.app.cover_tab.get_modul_text()
            if not modul_text:
                messagebox.showwarning("Validasi", "Input file modul terlebih dahulu di tab Cover.")
                return
            
            res, err = self.app.analysis_service.generate_penjelasan_singkat(
                judul,
                modul_text,
            )
            if err:
                messagebox.showerror("AI Error", err)
            else:
                penjelasan_text.delete("1.0", tk.END)
                penjelasan_text.insert("1.0", res)

        ttk.Button(action_row, text="✨ Penjelasan AI", style="Action.TButton", 
                   command=run_penjelasan_ai).pack(side="right")
        
        # 2. Input Area (Dinamis)
        content_frame = ttk.LabelFrame(left_pane, text=" Isi Konten ", padding=10)
        content_frame.pack(fill="both", expand=True)

        # Container Source Code
        self.kode_container = ttk.Frame(content_frame)
        self.kode_listbox = tk.Listbox(self.kode_container, height=6, font=("Consolas", 10))
        self.kode_listbox.pack(side="left", fill="both", expand=True)
        self.kode_listbox.drop_target_register(DND_FILES)
        self.kode_listbox.dnd_bind('<<Drop>>', self._on_kode_drop)
        k_btns = ttk.Frame(self.kode_container)
        k_btns.pack(side="right", padx=(5, 0))
        ttk.Button(k_btns, text="+", width=3, command=self._add_kode_logic).pack(pady=2)
        ttk.Button(k_btns, text="-", width=3, command=self._remove_kode_logic).pack()

        # Container Langkah Deskriptif
        self.langkah_container = ttk.Frame(content_frame)
        self.isi_a_text = scrolledtext.ScrolledText(self.langkah_container, height=6, font=("Segoe UI", 10))
        self.isi_a_text.pack(fill="both", expand=True)
        if initial_isi_a:
            self.isi_a_text.insert("1.0", initial_isi_a)
        ttk.Button(self.langkah_container, text="✨ Generate Langkah Kerja (AI)", style="Action.TButton", 
                   command=lambda: self._run_langkah_ai(judul_var, self.isi_a_text)).pack(fill="x", pady=(5,0))

        # 3. Lampiran Gambar (Selalu Muncul)
        img_frame = ttk.LabelFrame(left_pane, text=" Lampiran Gambar ", padding=10)
        img_frame.pack(fill="x", pady=(10, 0))
        img_main = ttk.Frame(img_frame)
        img_main.pack(fill="x")
        self.gambar_listbox = tk.Listbox(img_main, height=3, font=("Segoe UI", 9))
        self.gambar_listbox.pack(side="left", fill="both", expand=True)
        self.gambar_listbox.drop_target_register(DND_FILES)
        self.gambar_listbox.dnd_bind('<<Drop>>', self._on_gambar_drop)
        g_btns = ttk.Frame(img_main)
        g_btns.pack(side="right", padx=(5, 0))
        ttk.Button(g_btns, text="+", width=3, command=self._add_gambar_logic).pack(pady=2)
        ttk.Button(g_btns, text="📷", width=3, command=self._capture_gambar_logic).pack(pady=2)
        ttk.Button(g_btns, text="-", width=3, command=self._remove_gambar_logic).pack()

        # --- RIGHT PANE CONTENT (Analisa AI) ---
        ai_frame = ttk.LabelFrame(right_pane, text=" Hasil Analisa Hasil (AI) ", padding=10)
        ai_frame.pack(fill="both", expand=True)

        analisa_text = scrolledtext.ScrolledText(ai_frame, font=("Segoe UI", 10), bg="#ffffff")
        analisa_text.pack(fill="both", expand=True, pady=(0, 10))
        if initial_analisa:
            analisa_text.insert("1.0", initial_analisa)

        def run_ai():
            res, err = self.app.analysis_service.generate_analysis(
                tipe_var.get(), self.isi_a_text.get("1.0", tk.END),
                self.kode_items, self.gambar_items, self.app.cover_tab.get_template_choice(),
            )
            if err: messagebox.showerror("AI Error", err)
            else:
                analisa_text.delete("1.0", tk.END)
                analisa_text.insert("1.0", res)

        ttk.Button(ai_frame, text="🚀 Jalankan Analisa AI", style="Action.TButton", command=run_ai).pack(fill="x")

        # --- LOGIKA TAMPILAN (Toggle) ---
        def toggle_view(*args):
            self.kode_container.pack_forget()
            self.langkah_container.pack_forget()

            if tipe_var.get() == "1":
                self.kode_container.pack(fill="both", expand=True)
            else:
                self.langkah_container.pack(fill="both", expand=True)

        tipe_var.trace_add("write", toggle_view)
        toggle_view()
        self._refresh_dialog_lists()

        try:
            self.wait_window(dialog)
        finally:
            if self._active_bab1_dialog is dialog:
                self._active_bab1_dialog = None
        return res_val["data"]

    def _run_langkah_ai(self, judul_var, target_widget):
        judul = judul_var.get().strip()
        if not judul:
            messagebox.showwarning("Validasi", "Judul sub-bab belum diisi.")
            return

        modul_text = self.app.cover_tab.get_modul_text()

        image_path = self.gambar_items[0]["path"] if self.gambar_items else None
        if not modul_text and not image_path:
            image_path = filedialog.askopenfilename(
                title="Pilih Screenshot",
                filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")],
            )

        res, err = self.app.analysis_service.generate_langkah_kerja(
            judul, modul_text, image_path
        )
        if err:
            messagebox.showerror("AI Error", err)
            return
        target_widget.delete("1.0", tk.END)
        target_widget.insert("1.0", res)

    def _refresh_dialog_lists(self):
        if self.kode_listbox is not None:
            self.kode_listbox.delete(0, tk.END)
            for f in self.kode_items:
                # Menampilkan Judul kustom jika ada, jika tidak tampilkan nama file asli
                display_name = f.get("judul") or f.get("nama")
                self.kode_listbox.insert(tk.END, f"📄 {display_name}")

        if self.gambar_listbox is not None:
            self.gambar_listbox.delete(0, tk.END)
            for g in self.gambar_items:
                name = os.path.basename(g["path"])
                self.gambar_listbox.insert(
                    tk.END, f"🖼️ {name} ({g['caption']})"
                )
    def _on_kode_drop(self, event):
        # Mengambil data file yang di-drop
        files = self.kode_listbox.tk.splitlist(event.data)
        for file_path in files:
            # Filter ekstensi (opsional, bisa disesuaikan)
            ext = os.path.splitext(file_path)[1].lower()
            allowed = ['.py', '.c', '.cpp', '.java', '.js', '.html', '.css', '.php', '.sql', '.txt']
            
            if ext in allowed:
                self._show_title_popup_for_drop(file_path)
            else:
                messagebox.showwarning("File Tidak Didukung", f"File {os.path.basename(file_path)} bukan source code.")

    def _show_title_popup_for_drop(self, path):
        # Pop up input judul otomatis setelah file di-drop
        dialog = tk.Toplevel(self)
        dialog.title("Judul Source Code")
        dialog.geometry("400x150")
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self._active_bab1_dialog) # Menempel pada dialog editor
        dialog.grab_set()

        judul_var = tk.StringVar(value=os.path.basename(path)) # Default: nama file
        
        container = ttk.Frame(dialog, padding=15)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text=f"Masukkan Judul untuk:\n{os.path.basename(path)}", 
                  font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 5))
        
        entry = ttk.Entry(container, textvariable=judul_var)
        entry.pack(fill="x", pady=5)
        entry.focus_set()

        def save_dropped():
            judul = judul_var.get().strip()
            if not judul:
                messagebox.showwarning("Validasi", "Judul harus diisi!")
                return
            
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                self.kode_items.append({
                    "judul": judul,
                    "nama": os.path.basename(path),
                    "isi": content
                })
                self._refresh_dialog_lists()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membaca file: {e}")

        btn_frame = ttk.Frame(container)
        btn_frame.pack(side="bottom", fill="x", pady=(10, 0))
        
        ttk.Button(btn_frame, text="Tambahkan", style="Action.TButton", 
                   command=save_dropped).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Batal", command=dialog.destroy).pack(side="right")

    def _on_gambar_drop(self, event):
        # Mengambil data file yang di-drop
        files = self.gambar_listbox.tk.splitlist(event.data)
        for file_path in files:
            # Filter ekstensi gambar
            ext = os.path.splitext(file_path)[1].lower()
            allowed = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']

            if ext in allowed:
                self._show_caption_popup_for_drop(file_path)
            else:
                messagebox.showwarning("File Tidak Didukung",
                                       f"File {os.path.basename(file_path)} bukan file gambar yang didukung.")

    def _show_caption_popup_for_drop(self, path):
        # Pop up input caption otomatis setelah gambar di-drop
        dialog = tk.Toplevel(self)
        dialog.title("Caption Gambar")
        dialog.geometry("420x160")
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self._active_bab1_dialog)  # Menempel pada dialog editor
        dialog.grab_set()

        caption_var = tk.StringVar(value=os.path.basename(path))  # Default: nama file

        container = ttk.Frame(dialog, padding=15)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text=f"Masukkan Caption untuk:\n{os.path.basename(path)}",
                  font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 5))

        entry = ttk.Entry(container, textvariable=caption_var)
        entry.pack(fill="x", pady=5)
        entry.focus_set()

        def save_dropped():
            caption = caption_var.get().strip()
            if not caption:
                messagebox.showwarning("Validasi", "Caption harus diisi!")
                return

            self.gambar_items.append({
                "path": path,
                "caption": caption
            })
            self._refresh_dialog_lists()
            dialog.destroy()

        btn_frame = ttk.Frame(container)
        btn_frame.pack(side="bottom", fill="x", pady=(10, 0))

        ttk.Button(btn_frame, text="Tambahkan", style="Action.TButton",
                   command=save_dropped).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Batal", command=dialog.destroy).pack(side="right")

    def _add_kode_logic(self):
        # Membuat jendela pop-up dialog
        dialog = tk.Toplevel(self)
        dialog.title("Tambah Source Code")
        dialog.geometry("450x240")
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self)
        dialog.grab_set()

        judul_var = tk.StringVar()
        path_var = tk.StringVar()

        container = ttk.Frame(dialog, padding=20)
        container.pack(fill="both", expand=True)

        # Field Input Judul
        ttk.Label(container, text="Judul Source Code:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        ttk.Entry(container, textvariable=judul_var).pack(fill="x", pady=(5, 15))

        # Field Path File & Tombol Browse (...)
        ttk.Label(container, text="File Source Code:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        file_row = ttk.Frame(container)
        file_row.pack(fill="x", pady=5)
        
        path_ent = ttk.Entry(file_row, textvariable=path_var, state="readonly")
        path_ent.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def browse_file():
            path = filedialog.askopenfilename(
                title="Pilih File Source Code",
                filetypes=[
                    ("Source Code", "*.py;*.c;*.cpp;*.java;*.js;*.html;*.css;*.php;*.sql;*.txt"),
                    ("All Files", "*.*")
                ]
            )
            if path:
                path_var.set(path)

        ttk.Button(file_row, text="...", width=3, command=browse_file).pack(side="right")

        # Tombol Aksi
        btn_frame = ttk.Frame(container)
        btn_frame.pack(side="bottom", fill="x", pady=(10, 0))

        def on_save():
            judul = judul_var.get().strip()
            path = path_var.get().strip()
            
            if not judul or not path:
                messagebox.showwarning("Validasi", "Judul dan File harus diisi!")
                return
            
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Menyimpan data ke dalam list
                self.kode_items.append({
                    "judul": judul,
                    "nama": os.path.basename(path),
                    "isi": content
                })
                self._refresh_dialog_lists()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membaca file: {e}")

        ttk.Button(btn_frame, text="Simpan", style="Action.TButton", command=on_save).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Batal", command=dialog.destroy).pack(side="right")

    def _remove_kode_logic(self):
        sel = self.kode_listbox.curselection()
        if sel:
            self.kode_items.pop(sel[0])
            self._refresh_dialog_lists()

    def _add_gambar_logic(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png;*.jpg;*.jpeg")]
        )
        if path:
            cap = self._prompt_caption()
            if cap is not None:
                self.gambar_items.append({"path": path, "caption": cap})
                self._refresh_dialog_lists()

    def _capture_gambar_logic(self):
        main_window = self.winfo_toplevel()
        owner_dialog = self._active_bab1_dialog

        if owner_dialog is not None and not owner_dialog.winfo_exists():
            owner_dialog = None

        windows_to_hide = []
        if main_window.winfo_exists():
            windows_to_hide.append(main_window)
        if owner_dialog is not None and owner_dialog is not main_window:
            windows_to_hide.append(owner_dialog)

        previous_grab = None
        if owner_dialog is not None:
            try:
                current_grab = owner_dialog.grab_current()
                if current_grab is owner_dialog:
                    previous_grab = owner_dialog
                    owner_dialog.grab_release()
            except tk.TclError:
                previous_grab = None

        for window in windows_to_hide:
            try:
                window.withdraw()
                window.update_idletasks()
            except tk.TclError:
                continue

        def open_overlay():
            overlay = tk.Toplevel(main_window)
            overlay.attributes("-fullscreen", True)
            overlay.attributes("-topmost", True)
            overlay.attributes("-alpha", 0.28)
            overlay.configure(bg="black")
            overlay.grab_set()
            overlay.focus_force()

            hint_frame = ttk.Frame(overlay, padding=(12, 10))
            hint_frame.place(relx=1.0, x=-20, y=20, anchor="ne")
            ttk.Label(
                hint_frame,
                text="Drag untuk memilih area. ESC / klik kanan / Batal untuk keluar.",
            ).pack(side="left", padx=(0, 10))

            canvas = tk.Canvas(overlay, cursor="cross", bg="black", highlightthickness=0)
            canvas.pack(fill="both", expand=True)
            hint_frame.lift()

            state = {"start": None, "rect": None}
            restored = {"done": False}

            def restore_main_window():
                if restored["done"]:
                    return
                restored["done"] = True

                for window in windows_to_hide:
                    try:
                        window.deiconify()
                        window.lift()
                    except tk.TclError:
                        continue

                if previous_grab is not None and previous_grab.winfo_exists():
                    try:
                        previous_grab.grab_set()
                    except tk.TclError:
                        pass

                focus_target = owner_dialog if owner_dialog is not None and owner_dialog.winfo_exists() else main_window
                try:
                    focus_target.focus_force()
                except tk.TclError:
                    pass

            def cancel_capture(_event=None):
                try:
                    overlay.grab_release()
                except tk.TclError:
                    pass
                if overlay.winfo_exists():
                    overlay.destroy()
                restore_main_window()

            def on_press(event):
                state["start"] = (event.x, event.y)
                if state["rect"] is not None:
                    canvas.delete(state["rect"])
                state["rect"] = canvas.create_rectangle(
                    event.x,
                    event.y,
                    event.x,
                    event.y,
                    outline="#38bdf8",
                    width=2,
                )

            def on_drag(event):
                if not state["start"] or state["rect"] is None:
                    return
                sx, sy = state["start"]
                canvas.coords(state["rect"], sx, sy, event.x, event.y)

            def on_release(event):
                if not state["start"]:
                    cancel_capture()
                    return

                sx, sy = state["start"]
                ex, ey = event.x, event.y
                x1, x2 = sorted((sx, ex))
                y1, y2 = sorted((sy, ey))

                if (x2 - x1) < 5 or (y2 - y1) < 5:
                    cancel_capture()
                    return

                overlay.withdraw()
                overlay.update_idletasks()

                bbox = (x1, y1, x2, y2)
                try:
                    image = ImageGrab.grab(bbox=bbox)
                    screenshot_dir = os.path.join(tempfile.gettempdir(), "dglp_screenshots")
                    os.makedirs(screenshot_dir, exist_ok=True)
                    filename = f"screenshot_{time.time_ns()}.png"
                    screenshot_path = os.path.join(screenshot_dir, filename)
                    image.save(screenshot_path)

                    try:
                        overlay.grab_release()
                    except tk.TclError:
                        pass
                    overlay.destroy()
                    restore_main_window()

                    cap = self._prompt_caption()
                    if cap is not None:
                        self.gambar_items.append({"path": screenshot_path, "caption": cap})
                        self._refresh_dialog_lists()
                except Exception as e:
                    try:
                        overlay.grab_release()
                    except tk.TclError:
                        pass
                    if overlay.winfo_exists():
                        overlay.destroy()
                    restore_main_window()
                    messagebox.showerror("Error", f"Gagal mengambil screenshot: {e}")

            ttk.Button(hint_frame, text="Batal", command=cancel_capture).pack(side="right")

            canvas.bind("<ButtonPress-1>", on_press)
            canvas.bind("<B1-Motion>", on_drag)
            canvas.bind("<ButtonRelease-1>", on_release)
            overlay.bind("<Escape>", cancel_capture)
            overlay.bind("<Button-3>", cancel_capture)
            overlay.protocol("WM_DELETE_WINDOW", cancel_capture)

        # Memberi jeda singkat agar proses minimize selesai sebelum layar dicapture.
        self.after(200, open_overlay)

    def _remove_gambar_logic(self):
        sel = self.gambar_listbox.curselection()
        if sel:
            self.gambar_items.pop(sel[0])
            self._refresh_dialog_lists()

    def _prompt_caption(self):
        dialog = tk.Toplevel(self)
        dialog.title("Caption")
        dialog.geometry("420x160")
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self)
        dialog.grab_set()

        caption_var = tk.StringVar()
        ttk.Label(dialog, text="Caption").pack(anchor="w", padx=12, pady=8)
        ttk.Entry(dialog, textvariable=caption_var, width=48).pack(
            anchor="w", padx=12
        )

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