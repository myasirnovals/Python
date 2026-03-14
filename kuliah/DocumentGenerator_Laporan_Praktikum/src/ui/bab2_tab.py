import os
import tempfile
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext
from tkinterdnd2 import DND_FILES

from PIL import ImageGrab


class Bab2Tab(ttk.Frame):
    def __init__(self, app, parent):
        super().__init__(parent, padding=20)
        self.app = app
        self.bab2_items = []
        self._active_bab2_dialog = None

        self.bab2_deskripsi_text = None
        self.bab2_kode_items = []
        self.bab2_kode_container = None
        self.bab2_kode_listbox = None
        self.bab2_gambar_items = []
        self.bab2_gambar_listbox = None

        self._build()

    def _build(self):
        self.pack(fill="both", expand=True)

        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(
            header_frame,
            text="Daftar Tugas Praktikum",
            style="Header.TLabel",
        ).pack(side="left")

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="+ Tambah Sub-Bab Tugas", command=self._add_bab2).pack(
            side="left", padx=2
        )
        ttk.Button(btn_frame, text="✏️ Edit", command=self._edit_bab2).pack(
            side="left", padx=2
        )
        ttk.Button(btn_frame, text="🗑️ Hapus", command=self._remove_bab2).pack(
            side="left", padx=2
        )

        list_container = ttk.Frame(self)
        list_container.pack(fill="both", expand=True)

        self.bab2_listbox = tk.Listbox(
            list_container,
            font=("Segoe UI", 11),
            borderwidth=1,
            relief="flat",
            selectbackground="#007bff",
            highlightthickness=0,
            activestyle="none",
        )
        self.bab2_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            list_container, orient="vertical", command=self.bab2_listbox.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.bab2_listbox.config(yscrollcommand=scrollbar.set)

    def get_items(self):
        return self.bab2_items

    def fill_test_data(self):
        self.bab2_items = [
            {
                "judul_tugas": "Tugas 1: Validasi Input",
                "tipe_konten": "2",
                "isi_deskripsi": "Buat program yang menolak input kosong dan menampilkan pesan kesalahan.",
                "qa_items": [],
                "kode_items": [],
                "gambar_items": [],
                "isi_analisa_tugas": "Validasi memastikan data tidak kosong sebelum diproses lebih lanjut.",
            }
        ]
        self._refresh_bab2_list()

    def _refresh_bab2_list(self):
        self.bab2_listbox.delete(0, tk.END)
        for i, item in enumerate(self.bab2_items, 1):
            judul = item.get("judul_tugas") or item.get("judul_sub_bab") or f"Tugas {i}"
            tipe_konten = item.get("tipe_konten") or item.get("tipe") or "2"
            tipe = {
                "1": "Source Code",
                "2": "Langkah Kerja",
                "3": "Q & A",
            }.get(tipe_konten, "Langkah Kerja")
            self.bab2_listbox.insert(tk.END, f" {i}. {judul.upper()} — [{tipe}]")

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
        self._active_bab2_dialog = dialog
        dialog.title("Editor Tugas Praktikum")
        dialog.geometry("1020x600")
        dialog.minsize(900, 560)
        dialog.resizable(True, True)
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self)
        dialog.grab_set()

        data = initial.copy() if initial else {}
        tipe_var = tk.StringVar(value=data.get("tipe_konten") or data.get("tipe", "1"))
        judul_var = tk.StringVar(value=data.get("judul_tugas") or data.get("judul_sub_bab", ""))

        self.bab2_kode_items = data.get("kode_items") or data.get("list_kode") or data.get("kode_files", [])
        self.bab2_gambar_items = data.get("gambar_items") or data.get("list_gambar") or data.get("gambar_paths", [])
        
        self.qa_rows = [] 
        qa_initial_data = data.get("qa_items") or data.get("qa_list", [])

        # --- FOOTER NAVIGATION ---
        btn_row = ttk.Frame(dialog, padding=(15, 8))
        btn_row.pack(side="bottom", fill="x")
        ttk.Separator(dialog, orient="horizontal").pack(side="bottom", fill="x")

        res_val = {"data": None}

        def save():
            langkah_list = []
            if tipe_var.get() == "2":
                raw_text = self.bab2_deskripsi_text.get("1.0", "end-1c")
                langkah_list = [
                    {"nomor": i, "langkah_kerja": line.strip()}
                    for i, line in enumerate(raw_text.split("\n"), 1)
                    if line.strip()
                ]

            qa_list_final = []
            if tipe_var.get() == "3":
                for row in self.qa_rows:
                    q = row['q_entry'].get("1.0", "end-1c").strip()
                    a = row['a_entry'].get("1.0", "end-1c").strip()
                    if q or a:
                        qa_list_final.append({"pertanyaan": q, "jawaban": a})

            res_val["data"] = {
                "judul_tugas": judul_var.get(),
                "penjelasan_singkat": penjelasan_text.get("1.0", "end-1c"),
                "tipe_konten": tipe_var.get(),
                "isi_deskripsi": self.bab2_deskripsi_text.get("1.0", "end-1c"),
                "langkah_kerja_items": langkah_list,
                "qa_items": qa_list_final,
                "kode_items": self.bab2_kode_items,
                "gambar_items": self.bab2_gambar_items,
                "isi_analisa_tugas": analisa_text.get("1.0", "end-1c") if tipe_var.get() != "3" else "",
            }
            dialog.destroy()

        ttk.Button(btn_row, text="Simpan Ke Laporan", style="Action.TButton", command=save).pack(side="right", padx=5)
        ttk.Button(btn_row, text="Batal", command=dialog.destroy).pack(side="right")

        # --- BODY CONTAINER (Scroll + Responsive) ---
        body_host = ttk.Frame(dialog)
        body_host.pack(fill="both", expand=True)

        body_canvas = tk.Canvas(body_host, highlightthickness=0, bg="#f8f9fa")
        body_scrollbar = ttk.Scrollbar(body_host, orient="vertical", command=body_canvas.yview)
        body_canvas.configure(yscrollcommand=body_scrollbar.set)

        body_scrollbar.pack(side="right", fill="y")
        body_canvas.pack(side="left", fill="both", expand=True)

        scrollable_body = ttk.Frame(body_canvas, padding=12)
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

        # Gunakan frame biasa dengan pack agar kompatibel dengan toggle_view
        left_pane = ttk.Frame(main_container)
        left_pane.pack(side="left", fill="both", expand=True, padx=(0, 8))

        right_pane = ttk.Frame(main_container)
        # right_pane akan di-pack/unpack dinamis oleh toggle_view()

        # --- LEFT PANE ---
        info_frame = ttk.LabelFrame(left_pane, text=" Konfigurasi Tugas ", padding=10)
        info_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(info_frame, text="Topik Tugas:").pack(anchor="w")
        ttk.Entry(info_frame, textvariable=judul_var).pack(fill="x", pady=(2, 8))

        # 2. Penjelasan Singkat (Jangan di-pack di sini)
        self.penjelasan_frame = ttk.Frame(info_frame)
        ttk.Label(self.penjelasan_frame, text="Penjelasan Singkat:").pack(anchor="w")
        penjelasan_text = tk.Text(self.penjelasan_frame, height=3, font=("Segoe UI", 10), relief="solid", borderwidth=1)
        penjelasan_text.pack(fill="x", pady=(2, 8))
        initial_penjelasan = data.get("penjelasan_singkat", "")
        if initial_penjelasan:
            penjelasan_text.insert("1.0", initial_penjelasan)

        action_row = ttk.Frame(info_frame)

        type_area = ttk.Frame(action_row)
        type_area.pack(side="left")
        ttk.Label(type_area, text="Tipe Konten:").pack(side="left")
        ttk.Radiobutton(type_area, text="Source Code", variable=tipe_var, value="1").pack(side="left", padx=(10, 5))
        ttk.Radiobutton(type_area, text="Langkah Kerja", variable=tipe_var, value="2").pack(side="left", padx=5)
        ttk.Radiobutton(type_area, text="Q & A", variable=tipe_var, value="3").pack(side="left", padx=5)
        
        def run_penjelasan_ai():
            judul = judul_var.get().strip()
            if not judul:
                messagebox.showwarning("Validasi", "Isi Topik Tugas terlebih dahulu.")
                return

            modul_text = self.app.cover_tab.get_modul_text()
            if not modul_text:
                messagebox.showwarning("Validasi", "Input file modul terlebih dahulu di tab Cover.")
                return

            res, err = self.app.analysis_service.generate_penjelasan_singkat(
                judul,
                modul_text,
            )
            if err: messagebox.showerror("AI Error", err)
            else:
                penjelasan_text.delete("1.0", tk.END)
                penjelasan_text.insert("1.0", res)

        # Simpan ke variabel self agar bisa di-hide/show di toggle_view
        self.btn_ai_penjelasan = ttk.Button(action_row, text="✨ Penjelasan AI", style="Action.TButton", 
                                           command=run_penjelasan_ai)

        self.content_container = ttk.LabelFrame(left_pane, text=" Isi Konten ", padding=8)
        self.content_container.pack(fill="both", expand=True)

        # 1. Source Code View
        self.bab2_kode_container = ttk.Frame(self.content_container)
        self.bab2_kode_listbox = tk.Listbox(self.bab2_kode_container, height=6, font=("Consolas", 9))
        self.bab2_kode_listbox.pack(side="left", fill="both", expand=True)
        self.bab2_kode_listbox.drop_target_register(DND_FILES)
        self.bab2_kode_listbox.dnd_bind('<<Drop>>', self._on_kode_drop)
        k_btns = ttk.Frame(self.bab2_kode_container)
        k_btns.pack(side="right", padx=(5, 0))
        ttk.Button(k_btns, text="+", width=3, command=self._add_kode_logic).pack(pady=2)
        ttk.Button(k_btns, text="-", width=3, command=self._remove_kode_logic).pack()

        # 2. Deskriptif View
        self.langkah_container = ttk.Frame(self.content_container)
        self.bab2_deskripsi_text = scrolledtext.ScrolledText(self.langkah_container, height=6, font=("Segoe UI", 9))
        self.bab2_deskripsi_text.pack(fill="both", expand=True)
        initial_deskripsi = data.get("isi_deskripsi") or data.get("isi_a", "")
        if initial_deskripsi:
            self.bab2_deskripsi_text.insert("1.0", initial_deskripsi)
        ttk.Button(self.langkah_container, text="✨ Generate Langkah (AI)", style="Action.TButton",
                   command=lambda: self._run_langkah_ai(judul_var, self.bab2_deskripsi_text)).pack(fill="x", pady=(4,0))

        # 3. Q&A Table (DENGAN PENOMORAN DAN TOMBOL DI BAWAH)
        self.qa_table_container = ttk.Frame(self.content_container)
        
        # --- HEADER ---
        qa_header = ttk.Frame(self.qa_table_container, padding=(0, 0, 25, 0))
        qa_header.pack(fill="x", pady=(0, 5))
        qa_header.columnconfigure(0, weight=0, minsize=35) 
        qa_header.columnconfigure(1, weight=4)   # 40%
        qa_header.columnconfigure(2, weight=6)   # 60%
        qa_header.columnconfigure(3, weight=0, minsize=50)
        
        ttk.Label(qa_header, text="No.", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", padx=2)
        ttk.Label(qa_header, text="Pertanyaan", font=("Segoe UI", 9, "bold")).grid(row=0, column=1, sticky="w", padx=2)
        ttk.Label(qa_header, text="Jawaban", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky="w", padx=2)

        # --- TABLE AREA (Canvas & Scrollbar) ---
        table_body_frame = ttk.Frame(self.qa_table_container)
        table_body_frame.pack(fill="both", expand=True)

        qa_canvas = tk.Canvas(table_body_frame, highlightthickness=0, height=220)
        qa_scrollbar = ttk.Scrollbar(table_body_frame, orient="vertical", command=qa_canvas.yview)
        scrollable_table_frame = ttk.Frame(qa_canvas)
        canvas_frame_id = qa_canvas.create_window((0, 0), window=scrollable_table_frame, anchor="nw")

        def sync_width(event):
            qa_canvas.itemconfig(canvas_frame_id, width=event.width)
        
        qa_canvas.bind("<Configure>", sync_width)
        scrollable_table_frame.bind("<Configure>", lambda e: qa_canvas.configure(scrollregion=qa_canvas.bbox("all")))
        qa_canvas.configure(yscrollcommand=qa_scrollbar.set)
        
        qa_canvas.pack(side="left", fill="both", expand=True)
        qa_scrollbar.pack(side="right", fill="y")

        def renumber_qa():
            """Fungsi untuk memperbarui nomor urut"""
            for i, row in enumerate(self.qa_rows, 1):
                row['no_label'].config(text=f"{i}.")

        def add_qa_row(q_val="", a_val=""):
            row_frame = ttk.Frame(scrollable_table_frame)
            row_frame.pack(fill="x", expand=True, pady=2)
            row_frame.columnconfigure(0, weight=0, minsize=35)
            row_frame.columnconfigure(1, weight=4)
            row_frame.columnconfigure(2, weight=6)
            row_frame.columnconfigure(3, weight=0, minsize=50)

            # Label Nomor
            no_lbl = ttk.Label(row_frame, text="", font=("Segoe UI", 9))
            no_lbl.grid(row=0, column=0, sticky="nw", pady=5)

            q_ent = tk.Text(row_frame, height=2, width=30, font=("Segoe UI", 9), wrap="word")
            q_ent.insert("1.0", q_val)
            q_ent.grid(row=0, column=1, sticky="ew", padx=(0, 5))

            a_ent = tk.Text(row_frame, height=2, width=40, font=("Segoe UI", 9), wrap="word")
            a_ent.insert("1.0", a_val)
            a_ent.grid(row=0, column=2, sticky="ew", padx=(0, 5))

            def _on_delete():
                row_frame.destroy()
                # Hapus dari list self.qa_rows
                self.qa_rows[:] = [r for r in self.qa_rows if r['frame'] != row_frame]
                renumber_qa()

            btn_del = ttk.Button(row_frame, text="✕", width=3, command=_on_delete)
            btn_del.grid(row=0, column=3, sticky="ne", padx=(2, 5))

            # Simpan referensi ke list
            self.qa_rows.append({
                'frame': row_frame, 
                'no_label': no_lbl, 
                'q_entry': q_ent, 
                'a_entry': a_ent
            })
            renumber_qa()

        # --- TOOL BUTTONS (Pindah ke bawah) ---
        qa_tools = ttk.Frame(self.qa_table_container)
        qa_tools.pack(fill="x", pady=(10, 0))
        
        ttk.Button(qa_tools, text="+ Tambah Soal", command=add_qa_row).pack(side="left")
        
        def run_table_ai():
            modul_text = self.app.cover_tab.get_modul_text()
            if not modul_text:
                messagebox.showwarning("AI", "Input file modul terlebih dahulu di tab Cover!")
                return
            for row in self.qa_rows:
                q_text = row['q_entry'].get("1.0", "end-1c").strip()
                a_text = row['a_entry'].get("1.0", "end-1c").strip()
                if q_text and not a_text:
                    ans, err = self.app.analysis_service.answer_question(q_text, modul_text)
                    if not err: 
                        row['a_entry'].delete("1.0", tk.END)
                        row['a_entry'].insert("1.0", ans)

        ttk.Button(qa_tools, text="✨ AI Jawab", style="Action.TButton", command=run_table_ai).pack(side="left", padx=5)

        # 4. Gambar Section
        self.img_section = ttk.LabelFrame(left_pane, text=" Lampiran Gambar ", padding=8)
        img_main = ttk.Frame(self.img_section)
        img_main.pack(fill="x")
        self.bab2_gambar_listbox = tk.Listbox(img_main, height=3, font=("Segoe UI", 9))
        self.bab2_gambar_listbox.pack(side="left", fill="both", expand=True)
        self.bab2_gambar_listbox.drop_target_register(DND_FILES)
        self.bab2_gambar_listbox.dnd_bind('<<Drop>>', self._on_gambar_drop)
        g_btns = ttk.Frame(img_main)
        g_btns.pack(side="right", padx=(5, 0))
        ttk.Button(g_btns, text="+", width=3, command=self._add_gambar_logic).pack(pady=2)
        ttk.Button(g_btns, text="📷", width=3, command=self._capture_gambar_logic).pack(pady=2)
        ttk.Button(g_btns, text="-", width=3, command=self._remove_gambar_logic).pack()

        # --- RIGHT PANE ---
        self.ai_section = ttk.LabelFrame(right_pane, text=" Analisa Hasil (AI) ", padding=8)
        self.ai_section.pack(fill="both", expand=True)
        analisa_text = scrolledtext.ScrolledText(self.ai_section, font=("Segoe UI", 9), bg="#ffffff")
        analisa_text.pack(fill="both", expand=True, pady=(0, 8))
        initial_analisa = data.get("isi_analisa_tugas") or data.get("isi_analisa") or data.get("analisa", "")
        if initial_analisa:
            analisa_text.insert("1.0", initial_analisa)
        
        def run_ai():
            res, err = self.app.analysis_service.generate_analysis(
                tipe_var.get(), self.bab2_deskripsi_text.get("1.0", tk.END),
                self.bab2_kode_items, self.bab2_gambar_items, self.app.cover_tab.get_template_choice()
            )
            if err: messagebox.showerror("AI Error", err)
            else:
                analisa_text.delete("1.0", tk.END)
                analisa_text.insert("1.0", res)

        ttk.Button(self.ai_section, text="🚀 Generate Analisa AI", style="Action.TButton", command=run_ai).pack(fill="x")

        # --- TOGGLE LOGIC ---
        def toggle_view(*args):
            # 1. Sembunyikan elemen dinamis di bagian Info (Atas)
            self.penjelasan_frame.pack_forget()
            self.btn_ai_penjelasan.pack_forget()
            action_row.pack_forget()
            
            # 2. Sembunyikan elemen konten (Bawah)
            self.bab2_kode_container.pack_forget()
            self.langkah_container.pack_forget()
            self.qa_table_container.pack_forget()
            self.img_section.pack_forget()
            self.ai_section.pack_forget()
            right_pane.pack_forget()

            val = tipe_var.get()
            
            # 3. Atur Layout Atas (Khusus Q&A akan melewati bagian ini)
            if val != "3": 
                self.penjelasan_frame.pack(fill="x") # Munculkan Penjelasan Singkat
                self.btn_ai_penjelasan.pack(side="right") # Munculkan Tombol AI
            
            # Action row selalu muncul
            action_row.pack(fill="x", pady=5)

            # 4. Atur Layout Konten
            if val == "1":  # Source Code
                self.bab2_kode_container.pack(fill="both", expand=True)
                self.img_section.pack(fill="x", pady=(10, 0))
                right_pane.pack(side="right", fill="both", expand=True)
                self.ai_section.pack(fill="both", expand=True)
            elif val == "2":  # Langkah Kerja
                self.langkah_container.pack(fill="both", expand=True)
                self.img_section.pack(fill="x", pady=(10, 0))
                right_pane.pack(side="right", fill="both", expand=True)
                self.ai_section.pack(fill="both", expand=True)
            elif val == "3":  # Q & A
                # Area penjelasan otomatis kosong karena di-skip di langkah ke-3
                self.qa_table_container.pack(fill="both", expand=True)
                dialog.update_idletasks()
                qa_canvas.event_generate("<Configure>")

        tipe_var.trace_add("write", toggle_view)
        
        if qa_initial_data:
            for item in qa_initial_data:
                pertanyaan = item.get("pertanyaan") or item.get("q") or ""
                jawaban = item.get("jawaban") or item.get("a") or ""
                add_qa_row(pertanyaan, jawaban)
        else: add_qa_row()

        toggle_view()
        self._refresh_dialog_lists()
        try:
            self.wait_window(dialog)
        finally:
            if self._active_bab2_dialog is dialog:
                self._active_bab2_dialog = None
        return res_val["data"]

    def _run_langkah_ai(self, judul_var, target_widget):
        judul = judul_var.get().strip()
        if not judul:
            messagebox.showwarning("Validasi", "Judul sub-bab belum diisi.")
            return

        modul_text = self.app.cover_tab.get_modul_text()

        image_path = self.bab2_gambar_items[0]["path"] if self.bab2_gambar_items else None
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
        if self.bab2_kode_listbox is not None:
            self.bab2_kode_listbox.delete(0, tk.END)
            for f in self.bab2_kode_items:
                display_name = f.get("judul_kode") or f.get("judul") or f.get("nama_file") or f.get("nama")
                self.bab2_kode_listbox.insert(tk.END, f"📄 {display_name}")

        if self.bab2_gambar_listbox is not None:
            self.bab2_gambar_listbox.delete(0, tk.END)
            for g in self.bab2_gambar_items:
                name = os.path.basename(g["path"])
                caption = g.get("caption_gambar") or g.get("caption") or ""
                self.bab2_gambar_listbox.insert(
                    tk.END, f"🖼️ {name} ({caption})"
                )

    def _on_kode_drop(self, event):
        files = self.bab2_kode_listbox.tk.splitlist(event.data)
        for file_path in files:
            ext = os.path.splitext(file_path)[1].lower()
            allowed = ['.py', '.c', '.cpp', '.java', '.js', '.html', '.css', '.php', '.sql', '.txt']

            if ext in allowed:
                self._show_title_popup_for_drop(file_path)
            else:
                messagebox.showwarning("File Tidak Didukung", f"File {os.path.basename(file_path)} bukan source code.")

    def _show_title_popup_for_drop(self, path):
        dialog = tk.Toplevel(self)
        dialog.title("Judul Source Code")
        dialog.geometry("400x150")
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self._active_bab2_dialog)
        dialog.grab_set()

        judul_var = tk.StringVar(value=os.path.basename(path))

        container = ttk.Frame(dialog, padding=15)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text=f"Masukkan Judul untuk:\n{os.path.basename(path)}",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(0, 5))

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

                self.bab2_kode_items.append({
                    "judul_kode": judul,
                    "nama_file": os.path.basename(path),
                    "isi_kode": content,
                })
                self._refresh_dialog_lists()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membaca file: {e}")

        btn_frame = ttk.Frame(container)
        btn_frame.pack(side="bottom", fill="x", pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Tambahkan",
            style="Action.TButton",
            command=save_dropped,
        ).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Batal", command=dialog.destroy).pack(side="right")

    def _on_gambar_drop(self, event):
        files = self.bab2_gambar_listbox.tk.splitlist(event.data)
        for file_path in files:
            ext = os.path.splitext(file_path)[1].lower()
            allowed = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']

            if ext in allowed:
                self._show_caption_popup_for_drop(file_path)
            else:
                messagebox.showwarning(
                    "File Tidak Didukung",
                    f"File {os.path.basename(file_path)} bukan file gambar yang didukung.",
                )

    def _show_caption_popup_for_drop(self, path):
        dialog = tk.Toplevel(self)
        dialog.title("Caption Gambar")
        dialog.geometry("420x160")
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self._active_bab2_dialog)
        dialog.grab_set()

        caption_var = tk.StringVar(value=os.path.basename(path))

        container = ttk.Frame(dialog, padding=15)
        container.pack(fill="both", expand=True)

        ttk.Label(
            container,
            text=f"Masukkan Caption untuk:\n{os.path.basename(path)}",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(0, 5))

        entry = ttk.Entry(container, textvariable=caption_var)
        entry.pack(fill="x", pady=5)
        entry.focus_set()

        def save_dropped():
            caption = caption_var.get().strip()
            if not caption:
                messagebox.showwarning("Validasi", "Caption harus diisi!")
                return

            self.bab2_gambar_items.append({
                "path": path,
                "caption_gambar": caption,
            })
            self._refresh_dialog_lists()
            dialog.destroy()

        btn_frame = ttk.Frame(container)
        btn_frame.pack(side="bottom", fill="x", pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Tambahkan",
            style="Action.TButton",
            command=save_dropped,
        ).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Batal", command=dialog.destroy).pack(side="right")

    def _add_kode_logic(self):
        # Membuat jendela pop-up baru
        dialog = tk.Toplevel(self)
        dialog.title("Tambah Source Code")
        dialog.geometry("450x240")
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self)
        dialog.grab_set()

        judul_var = tk.StringVar()
        path_var = tk.StringVar()

        # Layout Container
        container = ttk.Frame(dialog, padding=20)
        container.pack(fill="both", expand=True)

        # Field Judul
        ttk.Label(container, text="Judul Source Code:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        ttk.Entry(container, textvariable=judul_var).pack(fill="x", pady=(5, 15))

        # Field Path File & Tombol Browse
        ttk.Label(container, text="File Source Code:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        file_row = ttk.Frame(container)
        file_row.pack(fill="x", pady=5)
        
        # Entry path dibuat readonly agar user hanya bisa lewat tombol browse
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

        # Tombol Aksi di Bawah
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
                
                # Simpan ke list dengan judul kustom
                self.bab2_kode_items.append({
                    "judul_kode": judul,
                    "nama_file": os.path.basename(path),
                    "isi_kode": content
                })
                self._refresh_dialog_lists()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membaca file: {e}")

        ttk.Button(btn_frame, text="Simpan", style="Action.TButton", command=on_save).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Batal", command=dialog.destroy).pack(side="right")

    def _remove_kode_logic(self):
        sel = self.bab2_kode_listbox.curselection()
        if sel:
            self.bab2_kode_items.pop(sel[0])
            self._refresh_dialog_lists()

    def _add_gambar_logic(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png;*.jpg;*.jpeg")]
        )
        if path:
            cap = self._prompt_caption()
            if cap is not None:
                self.bab2_gambar_items.append({"path": path, "caption_gambar": cap})
                self._refresh_dialog_lists()

    def _capture_gambar_logic(self):
        main_window = self.winfo_toplevel()
        owner_dialog = self._active_bab2_dialog

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
                        self.bab2_gambar_items.append({"path": screenshot_path, "caption_gambar": cap})
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

        self.after(200, open_overlay)

    def _remove_gambar_logic(self):
        sel = self.bab2_gambar_listbox.curselection()
        if sel:
            self.bab2_gambar_items.pop(sel[0])
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