"""code_image_tab.py - Reusable component for code and image management with drag-and-drop."""

import ctypes
import os
import tempfile
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
from tkinterdnd2 import DND_FILES

from PIL import ImageGrab

from ui.base import BaseTab
from ui.constants import (
    CONTENT_TYPE_SOURCE_CODE,
    CONTENT_TYPE_WORK_STEPS,
    CODE_EXTENSIONS,
    CODE_FILETYPE_PATTERN,
    MAX_CODE_FILE_SIZE,
    LABEL_SOURCE_CODE,
    LABEL_WORK_STEPS,
    EDITOR_DIALOG_WIDTH,
    EDITOR_DIALOG_HEIGHT,
    EDITOR_MIN_WIDTH,
    EDITOR_MIN_HEIGHT,
)
from ui.utils import extract_dnd_file_paths, parse_step_list


class CodeImageTab(BaseTab):
    """
    Reusable tab component for managing code files and images with drag-and-drop.
    
    Configuration:
        section_name: Display name (e.g., "Hasil Praktikum", "Tugas Praktikum")
        max_items: Maximum number of items allowed (None for unlimited)
    """
    
    def __init__(self, app, parent, section_name: str, max_items: int = None):
        self.section_name = section_name
        self.max_items = max_items
        self.items = []
        self._active_dialog = None
        self.main_tree = None
        self.quick_title_var = tk.StringVar()
        self.quick_type_var = tk.StringVar(value=CONTENT_TYPE_SOURCE_CODE)
        self.status_var = tk.StringVar(value="Siap. Tambahkan sub-bab dari panel Tambah Cepat.")
        self.current_edit_index = None

        self.detail_frame = None
        self.detail_judul_var = tk.StringVar()
        self.detail_tipe_var = tk.StringVar(value=CONTENT_TYPE_SOURCE_CODE)
        self.penjelasan_text = None
        self.analisa_text = None
        self.langkah_container = None
        
        # Dialog state
        self.kode_items = []
        self.gambar_items = []
        self.kode_listbox = None
        self.gambar_listbox = None
        self.kode_container = None
        self.gambar_container = None
        self.isi_a_text = None
        self.kode_title_var = tk.StringVar()
        self.gambar_caption_var = tk.StringVar()
        
        super().__init__(app, parent)
    
    def _build(self):
        """Build the tab UI."""
        self.pack_fill_expand()
        
        self._add_header(f"Daftar {self.section_name}", "Header.TLabel")

        ttk.Label(
            self,
            text="Prinsip IMK: alur sederhana, minim popup, dan feedback jelas di layar.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(0, 8))

        quick_add = ttk.LabelFrame(self, text=" Tambah Cepat Sub-Bab ", padding=10, style="Card.TLabelframe")
        quick_add.pack(fill="x", pady=(0, 8))
        quick_add.columnconfigure(1, weight=1)

        ttk.Label(quick_add, text="Judul").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Entry(quick_add, textvariable=self.quick_title_var).grid(row=0, column=1, sticky="ew")

        type_row = ttk.Frame(quick_add)
        type_row.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Label(type_row, text="Tipe").pack(side="left", padx=(0, 8))
        ttk.Radiobutton(
            type_row,
            text=LABEL_SOURCE_CODE,
            variable=self.quick_type_var,
            value=CONTENT_TYPE_SOURCE_CODE,
        ).pack(side="left", padx=(0, 10))
        ttk.Radiobutton(
            type_row,
            text=LABEL_WORK_STEPS,
            variable=self.quick_type_var,
            value=CONTENT_TYPE_WORK_STEPS,
        ).pack(side="left")

        ttk.Button(
            quick_add,
            text="Tambah Sub-Bab",
            style="Action.TButton",
            command=self._add_item,
        ).grid(row=0, column=2, rowspan=2, padx=(10, 0), sticky="ns")
        
        buttons = [
            ("Edit Detail", self._edit_item),
            ("Hapus Sub-Bab", self._remove_item),
        ]
        self._add_button_group(self, buttons, pady=10)
        
        list_container = ttk.LabelFrame(self, text=" Ringkasan Sub-Bab ", padding=10, style="Card.TLabelframe")
        list_container.pack(fill="both", expand=True)
        
        self.main_tree = ttk.Treeview(
            list_container,
            columns=("judul", "tipe", "kode", "gambar"),
            show="headings",
            height=12,
        )
        self.main_tree.heading("judul", text="Judul")
        self.main_tree.heading("tipe", text="Tipe")
        self.main_tree.heading("kode", text="Kode")
        self.main_tree.heading("gambar", text="Gambar")

        self.main_tree.column("judul", width=430, anchor="w")
        self.main_tree.column("tipe", width=130, anchor="center")
        self.main_tree.column("kode", width=90, anchor="center")
        self.main_tree.column("gambar", width=90, anchor="center")

        self.main_tree.pack(side="left", fill="both", expand=True)
        self.main_tree.bind("<Double-1>", lambda _e: self._edit_item())
        
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.main_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.main_tree.configure(yscrollcommand=scrollbar.set)

        ttk.Label(self, textvariable=self.status_var, style="Muted.TLabel").pack(anchor="w", pady=(8, 0))

        self.detail_frame = ttk.LabelFrame(
            self,
            text=" Editor Detail Sub-Bab ",
            padding=10,
            style="Card.TLabelframe",
        )

        # Header detail editor
        header_row = ttk.Frame(self.detail_frame)
        header_row.pack(fill="x", pady=(0, 6))
        ttk.Label(header_row, text="Judul Sub-Bab", style="Subheader.TLabel").pack(anchor="w")
        ttk.Entry(header_row, textvariable=self.detail_judul_var).pack(fill="x", pady=(2, 0))

        desc_row = ttk.Frame(self.detail_frame)
        desc_row.pack(fill="x", pady=(2, 6))
        ttk.Label(desc_row, text="Penjelasan Singkat", style="Subheader.TLabel").pack(anchor="w")
        self.penjelasan_text = tk.Text(desc_row, height=3, font=("Segoe UI", 10), relief="solid", borderwidth=1)
        self.penjelasan_text.pack(fill="x", pady=(2, 0))

        type_row = ttk.Frame(self.detail_frame)
        type_row.pack(fill="x", pady=(0, 8))
        ttk.Label(type_row, text="Tipe Konten", style="Subheader.TLabel").pack(side="left", padx=(0, 8))
        ttk.Radiobutton(
            type_row,
            text=LABEL_SOURCE_CODE,
            variable=self.detail_tipe_var,
            value=CONTENT_TYPE_SOURCE_CODE,
        ).pack(side="left", padx=(0, 10))
        ttk.Radiobutton(
            type_row,
            text=LABEL_WORK_STEPS,
            variable=self.detail_tipe_var,
            value=CONTENT_TYPE_WORK_STEPS,
        ).pack(side="left")

        action_row = ttk.Frame(self.detail_frame)
        action_row.pack(fill="x", pady=(0, 10))

        def run_penjelasan_ai_inline():
            judul = self.detail_judul_var.get().strip()
            if not judul:
                self.status_var.set("Isi judul sub-bab terlebih dahulu untuk generate penjelasan.")
                return

            modul_text = self.app.cover_tab.get_modul_text()
            if not modul_text:
                self.status_var.set("Modul belum diinput pada tab Cover.")
                return

            res, err = self.app.analysis_service.generate_penjelasan_singkat(judul, modul_text)
            if err:
                self.show_error("AI Error", err)
            else:
                self.penjelasan_text.delete("1.0", tk.END)
                self.penjelasan_text.insert("1.0", res)
                self.status_var.set("Penjelasan singkat berhasil digenerate.")

        ttk.Button(
            action_row,
            text="Generate Penjelasan AI",
            style="Action.TButton",
            command=run_penjelasan_ai_inline,
        ).pack(side="left")

        detail_split = ttk.Frame(self.detail_frame)
        detail_split.pack(fill="both", expand=True)

        left_pane = ttk.Frame(detail_split)
        left_pane.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right_pane = ttk.Frame(detail_split)
        right_pane.pack(side="right", fill="both", expand=True)

        content_frame = ttk.LabelFrame(left_pane, text=" Isi Konten ", padding=10, style="Card.TLabelframe")
        content_frame.pack(fill="both", expand=True)

        self.kode_container = ttk.Frame(content_frame)
        self.kode_listbox = tk.Listbox(self.kode_container, height=7, font=("Consolas", 10))
        self.kode_listbox.pack(side="left", fill="both", expand=True)
        self.kode_listbox.drop_target_register(DND_FILES)
        self.kode_listbox.dnd_bind("<<Drop>>", self._on_kode_drop)
        self.kode_listbox.bind("<<ListboxSelect>>", self._on_kode_select)

        k_btns = ttk.Frame(self.kode_container)
        k_btns.pack(side="right", padx=(5, 0))
        ttk.Button(k_btns, text="Tambah", command=self._add_kode).pack(fill="x", pady=(0, 4))
        ttk.Button(k_btns, text="Hapus", command=self._remove_kode).pack(fill="x")

        kode_edit = ttk.Frame(self.kode_container)
        kode_edit.pack(side="bottom", fill="x", pady=(6, 0))
        ttk.Label(kode_edit, text="Judul File", style="Subheader.TLabel").pack(anchor="w")
        ttk.Entry(kode_edit, textvariable=self.kode_title_var).pack(fill="x", pady=(2, 4))
        ttk.Button(kode_edit, text="Update Judul", command=self._apply_kode_title).pack(anchor="e")

        self.langkah_container = ttk.Frame(content_frame)
        self.isi_a_text = scrolledtext.ScrolledText(self.langkah_container, height=8, font=("Segoe UI", 10))
        self.isi_a_text.pack(fill="both", expand=True)
        ttk.Button(
            self.langkah_container,
            text="Generate Langkah Kerja AI",
            style="Action.TButton",
            command=lambda: self._run_langkah_ai(self.detail_judul_var),
        ).pack(fill="x", pady=(5, 0))

        img_frame = ttk.LabelFrame(left_pane, text=" Lampiran Gambar ", padding=10, style="Card.TLabelframe")
        img_frame.pack(fill="x", pady=(10, 0))
        img_main = ttk.Frame(img_frame)
        img_main.pack(fill="x")
        self.gambar_listbox = tk.Listbox(img_main, height=3, font=("Segoe UI", 9))
        self.gambar_listbox.pack(side="left", fill="both", expand=True)
        self.gambar_listbox.drop_target_register(DND_FILES)
        self.gambar_listbox.dnd_bind("<<Drop>>", self._on_gambar_drop)
        self.gambar_listbox.bind("<<ListboxSelect>>", self._on_gambar_select)

        g_btns = ttk.Frame(img_main)
        g_btns.pack(side="right", padx=(5, 0))
        ttk.Button(g_btns, text="Tambah", command=self._add_gambar).pack(fill="x", pady=(0, 4))
        ttk.Button(g_btns, text="Screenshot", command=self._capture_gambar).pack(fill="x", pady=(0, 4))
        ttk.Button(g_btns, text="Hapus", command=self._remove_gambar).pack(fill="x")

        gambar_edit = ttk.Frame(img_frame)
        gambar_edit.pack(fill="x", pady=(6, 0))
        ttk.Label(gambar_edit, text="Caption", style="Subheader.TLabel").pack(anchor="w")
        ttk.Entry(gambar_edit, textvariable=self.gambar_caption_var).pack(fill="x", pady=(2, 4))
        ttk.Button(gambar_edit, text="Update Caption", command=self._apply_gambar_caption).pack(anchor="e")

        ai_frame = ttk.LabelFrame(right_pane, text=" Hasil Analisa (AI) ", padding=10, style="Card.TLabelframe")
        ai_frame.pack(fill="both", expand=True)
        self.analisa_text = scrolledtext.ScrolledText(ai_frame, font=("Segoe UI", 10), bg="#ffffff")
        self.analisa_text.pack(fill="both", expand=True, pady=(0, 10))

        def run_ai_inline():
            res, err = self.app.analysis_service.generate_analysis(
                self.detail_tipe_var.get(),
                self.isi_a_text.get("1.0", tk.END),
                self.kode_items,
                self.gambar_items,
                self.app.cover_tab.get_template_choice(),
            )
            if err:
                self.show_error("AI Error", err)
            else:
                self.analisa_text.delete("1.0", tk.END)
                self.analisa_text.insert("1.0", res)
                self.status_var.set("Analisa AI berhasil diperbarui.")

        ttk.Button(
            ai_frame,
            text="Jalankan Analisa AI",
            style="Action.TButton",
            command=run_ai_inline,
        ).pack(fill="x")

        footer = ttk.Frame(self.detail_frame)
        footer.pack(fill="x", pady=(10, 0))
        ttk.Button(footer, text="Tutup Editor", command=self._cancel_inline_edit).pack(side="right")
        ttk.Button(
            footer,
            text="Simpan Perubahan",
            style="Action.TButton",
            command=self._save_inline_edit,
        ).pack(side="right", padx=(0, 6))

        self.detail_tipe_var.trace_add("write", lambda *_: self._toggle_detail_content())
    
    def get_items(self):
        """Get all items for report generation."""
        return self.items
    
    def fill_test_data(self):
        """Fill with test data for development."""
        self.items = [
            {
                "judul_sub_bab": "Percobaan 1: Percabangan",
                "tipe": CONTENT_TYPE_WORK_STEPS,
                "isi_a": "Jika nilai lebih besar dari 75 maka tampilkan LULUS.",
                "list_kode": [],
                "list_gambar": [],
                "isi_analisa": "Program memeriksa kondisi nilai dan menampilkan status sesuai aturan.",
            }
        ]
        self._refresh_list()
    
    def _refresh_list(self):
        """Refresh the main listbox display."""
        if self.main_tree is None:
            return

        for child in self.main_tree.get_children():
            self.main_tree.delete(child)

        for i, item in enumerate(self.items, 1):
            judul = item.get("judul_sub_bab") or f"Sub-Bab {i}"
            tipe = LABEL_SOURCE_CODE if item.get("tipe") == CONTENT_TYPE_SOURCE_CODE else LABEL_WORK_STEPS
            kode_count = len(item.get("list_kode") or [])
            gambar_count = len(item.get("list_gambar") or [])
            self.main_tree.insert(
                "",
                "end",
                iid=str(i - 1),
                values=(judul, tipe, str(kode_count), str(gambar_count)),
            )
    
    def _add_item(self):
        """Add new item inline without popup."""
        title = self.quick_title_var.get().strip()
        if not title:
            self.status_var.set("Judul sub-bab wajib diisi sebelum menambahkan.")
            return

        tipe = self.quick_type_var.get() or CONTENT_TYPE_SOURCE_CODE
        label_a = LABEL_SOURCE_CODE if tipe == CONTENT_TYPE_SOURCE_CODE else LABEL_WORK_STEPS
        self.items.append(
            {
                "judul_sub_bab": title,
                "penjelasan_singkat": "",
                "tipe": tipe,
                "label_point_a": label_a,
                "list_kode": [],
                "langkah_list": [],
                "list_gambar": [],
                "isi_analisa": "",
            }
        )
        self.quick_title_var.set("")
        self._refresh_list()
        last_index = len(self.items) - 1
        if self.main_tree is not None:
            self.main_tree.selection_set(str(last_index))
            self.main_tree.focus(str(last_index))
            self.main_tree.see(str(last_index))
        self.status_var.set("Sub-bab berhasil ditambahkan. Pilih Edit Detail untuk melengkapi isi.")
        self._start_inline_edit(last_index)
    
    def _edit_item(self):
        """Edit selected item."""
        index = self._selected_main_index()
        if index is None:
            self.status_var.set("Pilih satu sub-bab terlebih dahulu untuk diedit.")
            return
        self._start_inline_edit(index)
    
    def _remove_item(self):
        """Remove selected item."""
        index = self._selected_main_index()
        if index is None:
            self.status_var.set("Pilih satu sub-bab terlebih dahulu untuk dihapus.")
            return
        del self.items[index]
        self._refresh_list()
        self.status_var.set("Sub-bab dihapus.")
        if self.current_edit_index is not None and self.current_edit_index == index:
            self._cancel_inline_edit()

    def _start_inline_edit(self, index):
        """Open inline editor with selected item data."""
        if index < 0 or index >= len(self.items):
            return

        self.current_edit_index = index
        item = self.items[index]

        self.detail_judul_var.set(item.get("judul_sub_bab", ""))
        self.detail_tipe_var.set(item.get("tipe", CONTENT_TYPE_SOURCE_CODE))

        if self.penjelasan_text is not None:
            self.penjelasan_text.delete("1.0", tk.END)
            self.penjelasan_text.insert("1.0", item.get("penjelasan_singkat", ""))

        if self.isi_a_text is not None:
            initial_isi_a = item.get("isi_a", "")
            if not initial_isi_a:
                raw_langkah = item.get("langkah_list")
                if isinstance(raw_langkah, list):
                    rows = []
                    for idx, l_item in enumerate(raw_langkah, 1):
                        nomor = l_item.get("nomor", idx) if isinstance(l_item, dict) else idx
                        teks = l_item.get("langkah_kerja", "").strip() if isinstance(l_item, dict) else str(l_item).strip()
                        if teks:
                            rows.append(f"{nomor}. {teks}")
                    initial_isi_a = "\n".join(rows)
                elif isinstance(raw_langkah, str):
                    initial_isi_a = raw_langkah
            self.isi_a_text.delete("1.0", tk.END)
            self.isi_a_text.insert("1.0", initial_isi_a)

        if self.analisa_text is not None:
            self.analisa_text.delete("1.0", tk.END)
            self.analisa_text.insert("1.0", item.get("isi_analisa", ""))

        self.kode_items = [dict(k) for k in (item.get("list_kode") or [])]
        self.gambar_items = [dict(g) for g in (item.get("list_gambar") or [])]
        self._refresh_dialog_lists()
        self.kode_title_var.set("")
        self.gambar_caption_var.set("")

        self._toggle_detail_content()
        self.detail_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.status_var.set("Mode edit aktif. Ubah data lalu klik Simpan Perubahan.")

    def _save_inline_edit(self):
        """Persist inline editor content to selected item."""
        if self.current_edit_index is None:
            self.status_var.set("Tidak ada sub-bab yang sedang diedit.")
            return
        if self.current_edit_index >= len(self.items):
            self.status_var.set("Sub-bab yang diedit sudah tidak tersedia.")
            return

        judul = self.detail_judul_var.get().strip()
        if not judul:
            self.status_var.set("Judul sub-bab tidak boleh kosong.")
            return

        tipe = self.detail_tipe_var.get()
        label_a = LABEL_SOURCE_CODE if tipe == CONTENT_TYPE_SOURCE_CODE else LABEL_WORK_STEPS
        langkah_list = parse_step_list(self.isi_a_text.get("1.0", "end-1c")) if self.isi_a_text is not None else []

        self.items[self.current_edit_index] = {
            "judul_sub_bab": judul,
            "penjelasan_singkat": self.penjelasan_text.get("1.0", "end-1c") if self.penjelasan_text else "",
            "tipe": tipe,
            "label_point_a": label_a,
            "list_kode": self.kode_items,
            "langkah_list": langkah_list,
            "list_gambar": self.gambar_items,
            "isi_analisa": self.analisa_text.get("1.0", "end-1c") if self.analisa_text else "",
        }

        idx = self.current_edit_index
        self._refresh_list()
        if self.main_tree is not None:
            self.main_tree.selection_set(str(idx))
            self.main_tree.focus(str(idx))
            self.main_tree.see(str(idx))
        self.status_var.set("Perubahan sub-bab berhasil disimpan.")

    def _cancel_inline_edit(self):
        """Close inline editor panel."""
        self.current_edit_index = None
        if self.detail_frame is not None:
            self.detail_frame.pack_forget()
        self.status_var.set("Editor detail ditutup.")

    def _toggle_detail_content(self):
        """Show source-code area or work-step area based on selected type."""
        if self.kode_container is None or self.langkah_container is None:
            return

        self.kode_container.pack_forget()
        self.langkah_container.pack_forget()

        if self.detail_tipe_var.get() == CONTENT_TYPE_SOURCE_CODE:
            self.kode_container.pack(fill="both", expand=True)
        else:
            self.langkah_container.pack(fill="both", expand=True)

    def _selected_main_index(self):
        """Get selected row index from main tree."""
        if self.main_tree is None:
            return None
        selected = self.main_tree.selection()
        if not selected:
            return None
        try:
            return int(selected[0])
        except (ValueError, TypeError):
            return None
    
    def _open_editor_dialog(self, initial=None):
        """Open item editor dialog."""
        dialog = tk.Toplevel(self)
        self._active_dialog = dialog
        dialog.title(f"Editor {self.section_name}")
        dialog.geometry(f"{EDITOR_DIALOG_WIDTH}x{EDITOR_DIALOG_HEIGHT}")
        dialog.minsize(EDITOR_MIN_WIDTH, EDITOR_MIN_HEIGHT)
        dialog.resizable(True, True)
        dialog.configure(bg="#f3f6fb")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Initialize state
        data = initial.copy() if initial else {}
        tipe_var = tk.StringVar(value=data.get("tipe", CONTENT_TYPE_SOURCE_CODE))
        judul_var = tk.StringVar(value=data.get("judul_sub_bab", ""))
        self.kode_items = data.get("list_kode", [])
        self.gambar_items = data.get("list_gambar", [])
        
        initial_penjelasan = data.get("penjelasan_singkat", "")
        initial_isi_a = data.get("isi_a", "")
        if not initial_isi_a:
            raw_langkah = data.get("langkah_list")
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
        
        initial_analisa = data.get("isi_analisa", "")
        
        res_val = {"data": None}
        
        # Footer buttons
        btn_row = ttk.Frame(dialog, padding=(20, 10))
        btn_row.pack(side="bottom", fill="x")
        ttk.Separator(dialog, orient="horizontal").pack(side="bottom", fill="x")
        
        def save():
            raw_text = self.isi_a_text.get("1.0", "end-1c")
            langkah_list = parse_step_list(raw_text)
            
            label_a = LABEL_SOURCE_CODE if tipe_var.get() == CONTENT_TYPE_SOURCE_CODE else LABEL_WORK_STEPS
            
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
        
        # Body with scrollable canvas
        body_host = ttk.Frame(dialog)
        body_host.pack(fill="both", expand=True)
        
        body_canvas = tk.Canvas(body_host, highlightthickness=0, bg="#f8f9fa")
        body_scrollbar = ttk.Scrollbar(body_host, orient="vertical", command=body_canvas.yview)
        body_canvas.configure(yscrollcommand=body_scrollbar.set)
        
        body_scrollbar.pack(side="right", fill="y")
        body_canvas.pack(side="left", fill="both", expand=True)
        
        scrollable_body = ttk.Frame(body_canvas, padding=15)
        body_window = body_canvas.create_window((0, 0), window=scrollable_body, anchor="nw")
        
        scrollable_body.bind("<Configure>",
            lambda e: body_canvas.configure(scrollregion=body_canvas.bbox("all")))
        body_canvas.bind("<Configure>",
            lambda e: body_canvas.itemconfigure(body_window, width=e.width))
        
        def _on_mousewheel(event):
            body_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        body_canvas.bind("<Enter>", lambda e: body_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        body_canvas.bind("<Leave>", lambda e: body_canvas.unbind_all("<MouseWheel>"))
        
        main_container = ttk.Frame(scrollable_body)
        main_container.pack(fill="both", expand=True)
        
        content_split = ttk.Frame(main_container)
        content_split.pack(fill="both", expand=True)
        
        # Left pane: Input & Content
        left_pane = ttk.Frame(content_split)
        left_pane.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Right pane: Analysis
        right_pane = ttk.Frame(content_split)
        right_pane.pack(side="right", fill="both", expand=True)
        
        # --- LEFT PANE ---
        info_frame = ttk.LabelFrame(left_pane, text=" Informasi Dasar ", padding=10, style="Card.TLabelframe")
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
        
        type_row = ttk.Frame(action_row)
        type_row.pack(side="left")
        ttk.Label(type_row, text="Tipe Konten:").pack(side="left")
        ttk.Radiobutton(type_row, text=LABEL_SOURCE_CODE, variable=tipe_var, value=CONTENT_TYPE_SOURCE_CODE).pack(side="left", padx=10)
        ttk.Radiobutton(type_row, text=LABEL_WORK_STEPS, variable=tipe_var, value=CONTENT_TYPE_WORK_STEPS).pack(side="left")
        
        def run_penjelasan_ai():
            judul = judul_var.get().strip()
            if not judul:
                self.show_warning("Validasi", "Isi Judul Sub-Bab terlebih dahulu.")
                return
            
            modul_text = self.app.cover_tab.get_modul_text()
            if not modul_text:
                self.show_warning("Validasi", "Input file modul terlebih dahulu di tab Cover.")
                return
            
            res, err = self.app.analysis_service.generate_penjelasan_singkat(judul, modul_text)
            if err:
                self.show_error("AI Error", err)
            else:
                penjelasan_text.delete("1.0", tk.END)
                penjelasan_text.insert("1.0", res)
        
        ttk.Button(action_row, text="✨ Penjelasan AI", style="Action.TButton",
                   command=run_penjelasan_ai).pack(side="right")
        
        # Content frame
        content_frame = ttk.LabelFrame(left_pane, text=" Isi Konten ", padding=10, style="Card.TLabelframe")
        content_frame.pack(fill="both", expand=True)
        
        # Code container
        self.kode_container = ttk.Frame(content_frame)
        self.kode_listbox = tk.Listbox(self.kode_container, height=7, font=("Consolas", 10))
        self.kode_listbox.pack(side="left", fill="both", expand=True)
        self.kode_listbox.drop_target_register(DND_FILES)
        self.kode_listbox.dnd_bind('<<Drop>>', self._on_kode_drop)
        self.kode_listbox.bind("<<ListboxSelect>>", self._on_kode_select)

        k_btns = ttk.Frame(self.kode_container)
        k_btns.pack(side="right", padx=(5, 0))
        ttk.Button(k_btns, text="Tambah", command=self._add_kode).pack(fill="x", pady=(0, 4))
        ttk.Button(k_btns, text="Hapus", command=self._remove_kode).pack(fill="x")

        kode_edit = ttk.Frame(self.kode_container)
        kode_edit.pack(side="bottom", fill="x", pady=(6, 0))
        ttk.Label(kode_edit, text="Judul File", style="Subheader.TLabel").pack(anchor="w")
        ttk.Entry(kode_edit, textvariable=self.kode_title_var).pack(fill="x", pady=(2, 4))
        ttk.Button(kode_edit, text="Update Judul", command=self._apply_kode_title).pack(anchor="e")
        
        # Steps container
        self.langkah_container = ttk.Frame(content_frame)
        self.isi_a_text = scrolledtext.ScrolledText(self.langkah_container, height=6, font=("Segoe UI", 10))
        self.isi_a_text.pack(fill="both", expand=True)
        if initial_isi_a:
            self.isi_a_text.insert("1.0", initial_isi_a)
        ttk.Button(self.langkah_container, text="✨ Generate Langkah Kerja (AI)", style="Action.TButton",
                   command=lambda: self._run_langkah_ai(judul_var)).pack(fill="x", pady=(5, 0))
        
        # Image frame
        img_frame = ttk.LabelFrame(left_pane, text=" Lampiran Gambar ", padding=10, style="Card.TLabelframe")
        img_frame.pack(fill="x", pady=(10, 0))
        img_main = ttk.Frame(img_frame)
        img_main.pack(fill="x")
        self.gambar_listbox = tk.Listbox(img_main, height=3, font=("Segoe UI", 9))
        self.gambar_listbox.pack(side="left", fill="both", expand=True)
        self.gambar_listbox.drop_target_register(DND_FILES)
        self.gambar_listbox.dnd_bind('<<Drop>>', self._on_gambar_drop)
        self.gambar_listbox.bind("<<ListboxSelect>>", self._on_gambar_select)

        g_btns = ttk.Frame(img_main)
        g_btns.pack(side="right", padx=(5, 0))
        ttk.Button(g_btns, text="Tambah", command=self._add_gambar).pack(fill="x", pady=(0, 4))
        ttk.Button(g_btns, text="Screenshot", command=self._capture_gambar).pack(fill="x", pady=(0, 4))
        ttk.Button(g_btns, text="Hapus", command=self._remove_gambar).pack(fill="x")

        gambar_edit = ttk.Frame(img_frame)
        gambar_edit.pack(fill="x", pady=(6, 0))
        ttk.Label(gambar_edit, text="Caption", style="Subheader.TLabel").pack(anchor="w")
        ttk.Entry(gambar_edit, textvariable=self.gambar_caption_var).pack(fill="x", pady=(2, 4))
        ttk.Button(gambar_edit, text="Update Caption", command=self._apply_gambar_caption).pack(anchor="e")
        
        # --- RIGHT PANE ---
        ai_frame = ttk.LabelFrame(right_pane, text=" Hasil Analisa (AI) ", padding=10, style="Card.TLabelframe")
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
            if err:
                self.show_error("AI Error", err)
            else:
                analisa_text.delete("1.0", tk.END)
                analisa_text.insert("1.0", res)
        
        ttk.Button(ai_frame, text="Jalankan Analisa AI", style="Action.TButton", command=run_ai).pack(fill="x")
        
        # Toggle view based on content type
        def toggle_view(*args):
            self.kode_container.pack_forget()
            self.langkah_container.pack_forget()
            
            if tipe_var.get() == CONTENT_TYPE_SOURCE_CODE:
                self.kode_container.pack(fill="both", expand=True)
            else:
                self.langkah_container.pack(fill="both", expand=True)
        
        tipe_var.trace_add("write", toggle_view)
        toggle_view()
        self._refresh_dialog_lists()
        
        try:
            self.wait_window(dialog)
        finally:
            if self._active_dialog is dialog:
                self._active_dialog = None
        
        return res_val["data"]
    
    def _on_kode_drop(self, event):
        """Handle code file drop."""
        files = extract_dnd_file_paths(event)
        for file_path in files:
            if self._is_allowed_code_file(file_path):
                self._add_code_file(file_path, os.path.basename(file_path))
            else:
                self.show_warning("File Tidak Didukung", f"File {os.path.basename(file_path)} bukan source code.")
    
    def _on_gambar_drop(self, event):
        """Handle image file drop."""
        files = extract_dnd_file_paths(event)
        for file_path in files:
            if self._is_image_file(file_path):
                self.gambar_items.append({"path": file_path, "caption": os.path.basename(file_path)})
                self._refresh_dialog_lists()
            else:
                self.show_warning("File Tidak Didukung", f"File {os.path.basename(file_path)} bukan gambar yang didukung.")
    
    def _add_kode(self):
        """Add code file directly with minimal interaction."""
        path = filedialog.askopenfilename(
            title="Pilih File Source Code",
            filetypes=[
                ("Source Code", CODE_FILETYPE_PATTERN),
                ("All Files", "*.*"),
            ],
        )
        if not path:
            return

        self._add_code_file(path, os.path.basename(path))
    
    def _remove_kode(self):
        """Remove selected code file."""
        if self.kode_listbox.curselection():
            self.kode_items.pop(self.kode_listbox.curselection()[0])
            self._refresh_dialog_lists()
            self.kode_title_var.set("")
    
    def _add_gambar(self):
        """Add image via file dialog."""
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png;*.jpg;*.jpeg")]
        )
        if path:
            self.gambar_items.append({"path": path, "caption": os.path.basename(path)})
            self._refresh_dialog_lists()
    
    def _remove_gambar(self):
        """Remove selected image."""
        if self.gambar_listbox.curselection():
            self.gambar_items.pop(self.gambar_listbox.curselection()[0])
            self._refresh_dialog_lists()
            self.gambar_caption_var.set("")
    
    def _capture_gambar(self):
        """Capture screen region as image."""
        main_window = self.winfo_toplevel()
        owner_dialog = self._active_dialog
        
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
        
        # Get virtual screen dimensions
        try:
            user32 = ctypes.windll.user32
            virt_x = user32.GetSystemMetrics(76)
            virt_y = user32.GetSystemMetrics(77)
            virt_w = user32.GetSystemMetrics(78)
            virt_h = user32.GetSystemMetrics(79)
            if virt_w <= 0 or virt_h <= 0:
                raise ValueError("Invalid virtual screen size")
        except Exception:
            virt_x, virt_y = 0, 0
            virt_w = main_window.winfo_screenwidth()
            virt_h = main_window.winfo_screenheight()
        
        # Create semi-transparent overlay
        overlay = tk.Toplevel(main_window)
        overlay.overrideredirect(True)
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.28)
        overlay.configure(bg="black")
        overlay.geometry(f"{virt_w}x{virt_h}")
        overlay.update_idletasks()
        
        try:
            ctypes.windll.user32.SetWindowPos(
                overlay.winfo_id(), -1, virt_x, virt_y, virt_w, virt_h, 0x0010
            )
        except Exception:
            pass
        
        try:
            overlay.grab_set()
        except tk.TclError:
            pass
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
        
        state = {"start": None, "rect": None, "selection": None}
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
            state["rect"] = canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="white", width=2)
        
        def on_drag(event):
            if state["rect"] is not None and state["start"]:
                canvas.coords(state["rect"], state["start"][0], state["start"][1], event.x, event.y)
        
        def on_release(event):
            if state["start"]:
                x1, y1 = state["start"]
                x2, y2 = event.x, event.y
                state["selection"] = (min(x1, x2) + virt_x, min(y1, y2) + virt_y, max(x1, x2) + virt_x, max(y1, y2) + virt_y)
                perform_capture()
        
        def perform_capture():
            try:
                overlay.grab_release()
            except tk.TclError:
                pass
            overlay.destroy()
            restore_main_window()
            
            if state["selection"]:
                try:
                    bbox = state["selection"]
                    img = ImageGrab.grab(bbox=bbox)
                    fd, temp_path = tempfile.mkstemp(suffix='.png')
                    os.close(fd)
                    img.save(temp_path, 'PNG')

                    default_caption = f"Screenshot {len(self.gambar_items) + 1}"
                    self.gambar_items.append({"path": temp_path, "caption": default_caption})
                    self._refresh_dialog_lists()
                except Exception as e:
                    self.show_error("Capture Error", f"Gagal capture: {e}")
        
        canvas.bind("<Button-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        canvas.bind("<Escape>", cancel_capture)
        canvas.bind("<Button-3>", cancel_capture)
    
    def _add_code_file(self, path, title):
        """Read and append code file to current dialog list."""
        if not self._is_allowed_code_file(path):
            self.show_warning("File Tidak Didukung", "Ekstensi file tidak termasuk daftar source code yang diizinkan.")
            return
        try:
            content = self._read_code_file_safe(path)
            self.kode_items.append(
                {
                    "judul": title.strip() or os.path.basename(path),
                    "nama": os.path.basename(path),
                    "isi": content,
                }
            )
            self._refresh_dialog_lists()
        except Exception as e:
            self.show_error("Error", f"Gagal membaca file: {e}")
    
    def _refresh_dialog_lists(self):
        """Refresh dialog listboxes."""
        if self.kode_listbox is not None:
            self.kode_listbox.delete(0, tk.END)
            for f in self.kode_items:
                display_name = f.get("judul") or f.get("nama")
                self.kode_listbox.insert(tk.END, f"📄 {display_name}")
        
        if self.gambar_listbox is not None:
            self.gambar_listbox.delete(0, tk.END)
            for g in self.gambar_items:
                name = os.path.basename(g["path"])
                self.gambar_listbox.insert(tk.END, f"🖼️ {name} ({g['caption']})")

    def _on_kode_select(self, _event=None):
        """Bind selected code title to inline editor."""
        if not self.kode_listbox.curselection():
            self.kode_title_var.set("")
            return
        idx = self.kode_listbox.curselection()[0]
        current = self.kode_items[idx]
        self.kode_title_var.set(current.get("judul") or current.get("nama", ""))

    def _apply_kode_title(self):
        """Apply inline title update for selected code item."""
        if not self.kode_listbox.curselection():
            self.show_warning("Validasi", "Pilih file kode terlebih dahulu.")
            return
        idx = self.kode_listbox.curselection()[0]
        new_title = self.kode_title_var.get().strip()
        if not new_title:
            self.show_warning("Validasi", "Judul tidak boleh kosong.")
            return
        self.kode_items[idx]["judul"] = new_title
        self._refresh_dialog_lists()
        self.kode_listbox.selection_set(idx)

    def _on_gambar_select(self, _event=None):
        """Bind selected image caption to inline editor."""
        if not self.gambar_listbox.curselection():
            self.gambar_caption_var.set("")
            return
        idx = self.gambar_listbox.curselection()[0]
        self.gambar_caption_var.set(self.gambar_items[idx].get("caption", ""))

    def _apply_gambar_caption(self):
        """Apply inline caption update for selected image item."""
        if not self.gambar_listbox.curselection():
            self.show_warning("Validasi", "Pilih gambar terlebih dahulu.")
            return
        idx = self.gambar_listbox.curselection()[0]
        new_caption = self.gambar_caption_var.get().strip()
        if not new_caption:
            self.show_warning("Validasi", "Caption tidak boleh kosong.")
            return
        self.gambar_items[idx]["caption"] = new_caption
        self._refresh_dialog_lists()
        self.gambar_listbox.selection_set(idx)
    
    def _is_allowed_code_file(self, path):
        """Check if file extension is allowed for code."""
        ext = os.path.splitext(path)[1].lower()
        return ext in CODE_EXTENSIONS
    
    def _is_image_file(self, path):
        """Check if file is supported image format."""
        ext = os.path.splitext(path)[1].lower()
        return ext in {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'}
    
    def _read_code_file_safe(self, path):
        """Safely read code file content."""
        if not os.path.isfile(path):
            raise ValueError("Path file tidak valid.")
        
        if os.path.getsize(path) > MAX_CODE_FILE_SIZE:
            raise ValueError(f"Ukuran file terlalu besar (maksimal {MAX_CODE_FILE_SIZE / 1024 / 1024:.0f} MB).")
        
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        return content.replace("\x00", "")
    
    def _run_langkah_ai(self, judul_var):
        """Generate work steps using AI."""
        judul = judul_var.get().strip()
        if not judul:
            self.show_warning("Validasi", "Judul sub-bab belum diisi.")
            return
        
        modul_text = self.app.cover_tab.get_modul_text()
        image_path = self.gambar_items[0]["path"] if self.gambar_items else None
        
        if not modul_text and not image_path:
            image_path = filedialog.askopenfilename(
                title="Pilih Screenshot",
                filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")],
            )
        
        res, err = self.app.analysis_service.generate_langkah_kerja(judul, modul_text, image_path)
        if err:
            self.show_error("AI Error", err)
        else:
            self.isi_a_text.delete("1.0", tk.END)
            self.isi_a_text.insert("1.0", res)
