import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext


class Bab1Tab(ttk.Frame):
    def __init__(self, app, parent):
        super().__init__(parent, padding=20)
        self.app = app
        self.bab1_items = []
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
        dialog.title("Editor Langkah Kerja")
        dialog.geometry("950x850")
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self)
        dialog.grab_set()

        data = initial.copy() if initial else {}
        tipe_var = tk.StringVar(value=data.get("tipe", "1"))
        judul_var = tk.StringVar(value=data.get("judul_sub_bab", ""))

        btn_row = ttk.Frame(dialog, padding=(20, 10))
        btn_row.pack(side="bottom", fill="x")
        ttk.Separator(dialog, orient="horizontal").pack(
            side="bottom", fill="x", padx=20
        )

        res_val = {"data": None}

        def save():
            res_val["data"] = {
                "judul_sub_bab": judul_var.get(),
                "tipe": tipe_var.get(),
                "isi_a": self.isi_a_text.get("1.0", "end-1c"),
                "kode_files": self.kode_items,
                "gambar_paths": self.gambar_items,
                "analisa": analisa_text.get("1.0", "end-1c"),
            }
            dialog.destroy()

        ttk.Button(
            btn_row, text="Simpan Ke Laporan", style="Action.TButton", command=save
        ).pack(side="right", padx=5)
        ttk.Button(btn_row, text="Batal", command=dialog.destroy).pack(side="right")

        container = ttk.Frame(dialog, padding=20)
        container.pack(side="top", fill="both", expand=True)

        info_frame = ttk.LabelFrame(container, text=" Informasi Dasar ", padding=15)
        info_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(info_frame, text="Judul Sub-Bab:").grid(row=0, column=0, sticky="w")
        ttk.Entry(info_frame, textvariable=judul_var, width=70).grid(
            row=0, column=1, padx=10, sticky="ew"
        )

        type_choice_frame = ttk.Frame(info_frame)
        type_choice_frame.grid(row=1, column=1, sticky="w", pady=(10, 0))
        ttk.Label(info_frame, text="Tipe Konten:").grid(
            row=1, column=0, sticky="w", pady=(10, 0)
        )
        ttk.Radiobutton(
            type_choice_frame, text="Source Code", variable=tipe_var, value="1"
        ).pack(side="left")
        ttk.Radiobutton(
            type_choice_frame, text="Langkah Deskriptif", variable=tipe_var, value="2"
        ).pack(side="left", padx=20)

        modul_frame = ttk.Frame(info_frame)
        ttk.Label(modul_frame, text="File Modul:").pack(side="left")
        ttk.Entry(modul_frame, textvariable=self.modul_path_var, width=50).pack(
            side="left", padx=10
        )
        ttk.Button(modul_frame, text="Browse", command=self._browse_modul).pack(
            side="left", padx=2
        )
        ttk.Button(modul_frame, text="Muat", command=self._load_modul_text).pack(
            side="left"
        )

        content_frame = ttk.LabelFrame(container, text=" Isi & Dokumentasi ", padding=15)
        content_frame.pack(fill="both", expand=True)

        self.isi_a_text = scrolledtext.ScrolledText(
            content_frame, height=6, font=("Segoe UI", 10)
        )
        if data.get("isi_a"):
            self.isi_a_text.insert("1.0", data.get("isi_a"))

        langkah_toolbar = ttk.Frame(content_frame)
        ttk.Button(
            langkah_toolbar,
            text="✨ Generate Langkah Kerja (AI)",
            style="Action.TButton",
            command=lambda: self._run_langkah_ai(judul_var, self.isi_a_text),
        ).pack(side="left", pady=(0, 5))

        self.kode_items = data.get("kode_files", [])
        self.kode_container = ttk.Frame(content_frame)
        self.kode_listbox = tk.Listbox(
            self.kode_container, height=6, font=("Consolas", 10)
        )
        self.kode_listbox.pack(side="left", fill="both", expand=True)

        k_btns = ttk.Frame(self.kode_container)
        k_btns.pack(side="right", padx=(10, 0))
        ttk.Button(k_btns, text="Tambah Kode", command=self._add_kode_logic).pack(
            fill="x", pady=2
        )
        ttk.Button(k_btns, text="Hapus", command=self._remove_kode_logic).pack(
            fill="x"
        )

        img_label = ttk.Label(
            content_frame, text="Lampiran Gambar:", style="Subheader.TLabel"
        )
        img_label.pack(anchor="w", pady=(10, 5))

        self.gambar_items = data.get("gambar_paths", [])
        img_main = ttk.Frame(content_frame)
        img_main.pack(fill="x")

        self.gambar_listbox = tk.Listbox(img_main, height=3, font=("Segoe UI", 9))
        self.gambar_listbox.pack(side="left", fill="both", expand=True)

        g_btns = ttk.Frame(img_main)
        g_btns.pack(side="right", padx=(10, 0))
        ttk.Button(g_btns, text="+ Gambar", command=self._add_gambar_logic).pack(
            fill="x", pady=2
        )
        ttk.Button(g_btns, text="Hapus", command=self._remove_gambar_logic).pack(
            fill="x"
        )

        ai_frame = ttk.LabelFrame(container, text=" Analisa Hasil (AI) ", padding=15)
        ai_frame.pack(fill="both", expand=True, pady=(10, 0))

        analisa_text = scrolledtext.ScrolledText(
            ai_frame, height=5, font=("Segoe UI", 10), bg="#fcfcfc"
        )
        analisa_text.pack(fill="both", expand=True)
        if data.get("analisa"):
            analisa_text.insert("1.0", data.get("analisa"))

        def run_ai():
            res, err = self.app.analysis_service.generate_analysis(
                tipe_var.get(),
                self.isi_a_text.get("1.0", tk.END),
                self.kode_items,
                self.gambar_items,
                self.app.cover_tab.get_template_choice(),
            )
            if err:
                messagebox.showerror("AI Error", err)
            else:
                analisa_text.delete("1.0", tk.END)
                analisa_text.insert("1.0", res)

        ttk.Button(
            ai_frame,
            text="✨ Generate Analisa Otomatis",
            style="Action.TButton",
            command=run_ai,
        ).pack(pady=5)

        def toggle_view(*args):
            modul_frame.grid_forget()
            langkah_toolbar.pack_forget()
            self.isi_a_text.pack_forget()
            self.kode_container.pack_forget()

            if tipe_var.get() == "1":
                self.kode_container.pack(fill="both", expand=True)
            else:
                modul_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))
                langkah_toolbar.pack(anchor="w")
                self.isi_a_text.pack(fill="both", expand=True)

        tipe_var.trace_add("write", toggle_view)
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