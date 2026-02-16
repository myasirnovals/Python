import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext


class Bab2Tab(ttk.Frame):
    def __init__(self, app, parent):
        super().__init__(parent, padding=20)
        self.app = app
        self.bab2_items = []
        self.modul_path_var = tk.StringVar()
        self.modul_text_cache = ""
        self.modul_loaded_path = ""

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

    def _refresh_bab2_list(self):
        self.bab2_listbox.delete(0, tk.END)
        for i, item in enumerate(self.bab2_items, 1):
            judul = item.get("judul_sub_bab") or f"Tugas {i}"
            tipe = "Source Code" if item.get("tipe") == "1" else "Langkah Kerja"
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
        dialog.title("Editor Tugas Praktikum")
        dialog.geometry("1020x600")
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self)
        dialog.grab_set()

        data = initial.copy() if initial else {}
        tipe_var = tk.StringVar(value=data.get("tipe", "1"))
        judul_var = tk.StringVar(value=data.get("judul_sub_bab", ""))
        
        self.qa_rows = [] 
        qa_initial_data = data.get("qa_list", [])

        # --- FOOTER NAVIGATION ---
        btn_row = ttk.Frame(dialog, padding=(15, 8))
        btn_row.pack(side="bottom", fill="x")
        ttk.Separator(dialog, orient="horizontal").pack(side="bottom", fill="x")

        res_val = {"data": None}

        def save():
            qa_list_final = []
            if tipe_var.get() == "3":
                for row in self.qa_rows:
                    q = row['q_entry'].get("1.0", "end-1c").strip()
                    a = row['a_entry'].get("1.0", "end-1c").strip()
                    if q or a:
                        qa_list_final.append({"q": q, "a": a})

            res_val["data"] = {
                "judul_sub_bab": judul_var.get(),
                "tipe": tipe_var.get(),
                "isi_a": self.isi_a_text.get("1.0", "end-1c"),
                "qa_list": qa_list_final,
                "kode_files": self.kode_items,
                "gambar_paths": self.gambar_items,
                "analisa": analisa_text.get("1.0", "end-1c") if tipe_var.get() != "3" else ""
            }
            dialog.destroy()

        ttk.Button(btn_row, text="Simpan Ke Laporan", style="Action.TButton", command=save).pack(side="right", padx=5)
        ttk.Button(btn_row, text="Batal", command=dialog.destroy).pack(side="right")

        # --- BODY CONTAINER ---
        main_container = ttk.Frame(dialog, padding=12)
        main_container.pack(fill="both", expand=True)

        left_pane = ttk.Frame(main_container)
        left_pane.pack(side="left", fill="both", expand=True)

        right_pane = ttk.Frame(main_container)

        # --- LEFT PANE ---
        info_frame = ttk.LabelFrame(left_pane, text=" Konfigurasi Tugas ", padding=8)
        info_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(info_frame, text="Topik Tugas:").pack(anchor="w")
        ttk.Entry(info_frame, textvariable=judul_var).pack(fill="x", pady=(2, 5))

        type_row = ttk.Frame(info_frame)
        type_row.pack(fill="x", pady=2)
        ttk.Radiobutton(type_row, text="Source Code", variable=tipe_var, value="1").pack(side="left")
        ttk.Radiobutton(type_row, text="Deskriptif", variable=tipe_var, value="2").pack(side="left", padx=10)
        ttk.Radiobutton(type_row, text="Q & A", variable=tipe_var, value="3").pack(side="left")

        self.modul_frame = ttk.Frame(info_frame)
        ttk.Label(self.modul_frame, text="Modul:").pack(side="left")
        ttk.Entry(self.modul_frame, textvariable=self.modul_path_var, width=20).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(self.modul_frame, text="...", width=3, command=self._browse_modul).pack(side="left", padx=2)
        ttk.Button(self.modul_frame, text="Muat", width=5, command=self._load_modul_text).pack(side="left")

        self.content_container = ttk.LabelFrame(left_pane, text=" Isi Konten ", padding=8)
        self.content_container.pack(fill="both", expand=True)

        # 1. Source Code View
        self.kode_container = ttk.Frame(self.content_container)
        self.kode_listbox = tk.Listbox(self.kode_container, height=6, font=("Consolas", 9))
        self.kode_listbox.pack(side="left", fill="both", expand=True)
        k_btns = ttk.Frame(self.kode_container)
        k_btns.pack(side="right", padx=(5, 0))
        ttk.Button(k_btns, text="+", width=3, command=self._add_kode_logic).pack(pady=2)
        ttk.Button(k_btns, text="-", width=3, command=self._remove_kode_logic).pack()

        # 2. Deskriptif View
        self.langkah_container = ttk.Frame(self.content_container)
        self.isi_a_text = scrolledtext.ScrolledText(self.langkah_container, height=6, font=("Segoe UI", 9))
        self.isi_a_text.pack(fill="both", expand=True)
        ttk.Button(self.langkah_container, text="✨ Generate Langkah (AI)", style="Action.TButton",
                   command=lambda: self._run_langkah_ai(judul_var, self.isi_a_text)).pack(fill="x", pady=(4,0))

        # 3. Q&A Table (DENGAN PENOMORAN DAN TOMBOL DI BAWAH)
        self.qa_table_container = ttk.Frame(self.content_container)
        
        # --- HEADER ---
        qa_header = ttk.Frame(self.qa_table_container)
        qa_header.pack(fill="x", pady=(0, 5))
        qa_header.columnconfigure(0, minsize=35) # Kolom No
        qa_header.columnconfigure(1, weight=2)   # Kolom Pertanyaan
        qa_header.columnconfigure(2, weight=3)   # Kolom Jawaban
        qa_header.columnconfigure(3, minsize=50) # Kolom Hapus
        
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
            row_frame.columnconfigure(0, minsize=35)
            row_frame.columnconfigure(1, weight=2)
            row_frame.columnconfigure(2, weight=3)
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
            if not self.modul_text_cache:
                messagebox.showwarning("AI", "Muat modul terlebih dahulu!")
                return
            for row in self.qa_rows:
                q_text = row['q_entry'].get("1.0", "end-1c").strip()
                a_text = row['a_entry'].get("1.0", "end-1c").strip()
                if q_text and not a_text:
                    ans, err = self.app.analysis_service.answer_question(q_text, self.modul_text_cache)
                    if not err: 
                        row['a_entry'].delete("1.0", tk.END)
                        row['a_entry'].insert("1.0", ans)

        ttk.Button(qa_tools, text="✨ AI Jawab", style="Action.TButton", command=run_table_ai).pack(side="left", padx=5)

        # 4. Gambar Section
        self.img_section = ttk.LabelFrame(left_pane, text=" Lampiran Gambar ", padding=8)
        img_main = ttk.Frame(self.img_section)
        img_main.pack(fill="x")
        self.gambar_listbox = tk.Listbox(img_main, height=3, font=("Segoe UI", 9))
        self.gambar_listbox.pack(side="left", fill="both", expand=True)
        g_btns = ttk.Frame(img_main)
        g_btns.pack(side="right", padx=(5, 0))
        ttk.Button(g_btns, text="+", width=3, command=self._add_gambar_logic).pack(pady=2)
        ttk.Button(g_btns, text="-", width=3, command=self._remove_gambar_logic).pack()

        # --- RIGHT PANE ---
        self.ai_section = ttk.LabelFrame(right_pane, text=" Analisa Hasil (AI) ", padding=8)
        self.ai_section.pack(fill="both", expand=True)
        analisa_text = scrolledtext.ScrolledText(self.ai_section, font=("Segoe UI", 9), bg="#ffffff")
        analisa_text.pack(fill="both", expand=True, pady=(0, 8))
        if data.get("analisa"): analisa_text.insert("1.0", data.get("analisa"))
        
        def run_ai():
            res, err = self.app.analysis_service.generate_analysis(
                tipe_var.get(), self.isi_a_text.get("1.0", tk.END),
                self.kode_items, self.gambar_items, self.app.cover_tab.get_template_choice()
            )
            if err: messagebox.showerror("AI Error", err)
            else:
                analisa_text.delete("1.0", tk.END)
                analisa_text.insert("1.0", res)

        ttk.Button(self.ai_section, text="🚀 Generate Analisa AI", style="Action.TButton", command=run_ai).pack(fill="x")

        # --- TOGGLE LOGIC ---
        def toggle_view(*args):
            self.modul_frame.pack_forget()
            self.kode_container.pack_forget()
            self.langkah_container.pack_forget()
            self.qa_table_container.pack_forget()
            self.img_section.pack_forget()
            self.ai_section.pack_forget()
            right_pane.pack_forget()

            val = tipe_var.get()
            if val == "1":
                right_pane.pack(side="right", fill="both", expand=True, padx=(8, 0))
                self.kode_container.pack(fill="both", expand=True)
                self.img_section.pack(fill="x", pady=(8, 0))
                self.ai_section.pack(fill="both", expand=True)
            elif val == "2":
                right_pane.pack(side="right", fill="both", expand=True, padx=(8, 0))
                self.modul_frame.pack(fill="x", pady=4)
                self.langkah_container.pack(fill="both", expand=True)
                self.img_section.pack(fill="x", pady=(8, 0))
                self.ai_section.pack(fill="both", expand=True)
            elif val == "3":
                self.modul_frame.pack(fill="x", pady=4)
                self.qa_table_container.pack(fill="both", expand=True)
                # Sinkronisasi ulang lebar setelah panel Q&A muncul
                dialog.after(100, lambda: qa_canvas.event_generate("<Configure>"))

        tipe_var.trace_add("write", toggle_view)
        
        if qa_initial_data:
            for item in qa_initial_data: add_qa_row(item['q'], item['a'])
        else: add_qa_row()

        toggle_view()
        self._refresh_dialog_lists()
        self.wait_window(dialog)
        return res_val["data"]

    def _browse_modul(self):
        path = filedialog.askopenfilename(
            title="Pilih File Modul",
            filetypes=[("Dokumen", "*.pdf;*.docx")],
        )
        if path:
            self.modul_path_var.set(path)

    def _load_modul_text(self):
        path = self.modul_path_var.get().strip()
        if not path:
            messagebox.showwarning("Validasi", "Path file modul belum diisi.")
            return
        text = self.app.analysis_service.read_modul_text(path)
        if not text:
            messagebox.showwarning("Modul", "Modul kosong atau gagal dibaca.")
            return
        self.modul_text_cache = text
        self.modul_loaded_path = path
        messagebox.showinfo("Modul", f"Modul berhasil dimuat ({len(text)} karakter).")

    def _run_langkah_ai(self, judul_var, target_widget):
        judul = judul_var.get().strip()
        if not judul:
            messagebox.showwarning("Validasi", "Judul sub-bab belum diisi.")
            return

        modul_path = self.modul_path_var.get().strip()
        if modul_path and modul_path != self.modul_loaded_path:
            self._load_modul_text()

        image_path = self.gambar_items[0]["path"] if self.gambar_items else None
        if not self.modul_text_cache and not image_path:
            image_path = filedialog.askopenfilename(
                title="Pilih Screenshot",
                filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")],
            )

        res, err = self.app.analysis_service.generate_langkah_kerja(
            judul, self.modul_text_cache, image_path
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
                self.kode_listbox.insert(tk.END, f"📄 {f['nama']}")

        if self.gambar_listbox is not None:
            self.gambar_listbox.delete(0, tk.END)
            for g in self.gambar_items:
                name = os.path.basename(g["path"])
                self.gambar_listbox.insert(
                    tk.END, f"🖼️ {name} ({g['caption']})"
                )

    def _add_kode_logic(self):
        paths = filedialog.askopenfilenames(
            title="Pilih File Source Code",
            filetypes=[
                (
                    "Source Code",
                    "*.py;*.c;*.cpp;*.java;*.js;*.html;*.css;*.php;*.sql;*.txt",
                ),
                ("All Files", "*.*"),
            ],
        )

        if not paths:
            return

        for path in paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                nama_file = os.path.basename(path)
                self.kode_items.append({"nama": nama_file, "isi": content})
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Gagal membaca file {os.path.basename(path)}: {e}"
                )

        self._refresh_dialog_lists()

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