"""CodeImageTab class implementation."""

import tkinter as tk
from tkinter import scrolledtext, ttk

from tkinterdnd2 import DND_FILES

from ui.core.base_tab import BaseTab
from ui.constants import (
    CONTENT_TYPE_Q_AND_A,
    CONTENT_TYPE_SOURCE_CODE,
    CONTENT_TYPE_WORK_STEPS,
    LABEL_Q_AND_A,
    LABEL_SOURCE_CODE,
    LABEL_WORK_STEPS,
)

from .ai_mixin import CodeImageAIMixin
from .attachments_mixin import CodeImageAttachmentsMixin
from .items_mixin import CodeImageItemsMixin
from .qa_mixin import CodeImageQAMixin


class CodeImageTab(
    CodeImageItemsMixin,
    CodeImageAttachmentsMixin,
    CodeImageQAMixin,
    CodeImageAIMixin,
    BaseTab,
):
    """Reusable tab component for managing code files and images."""

    def __init__(self, app, parent, section_name: str, max_items: int = None):
        self.section_name = section_name
        self.max_items = max_items
        self.items = []
        self.main_tree = None
        self.quick_title_var = tk.StringVar()
        self.quick_type_var = tk.StringVar(value=CONTENT_TYPE_SOURCE_CODE)
        self.status_var = tk.StringVar(
            value="Siap. Tambahkan sub-bab dari panel Tambah Cepat."
        )
        self.current_edit_index = None

        self.detail_frame = None
        self.detail_judul_var = tk.StringVar()
        self.detail_tipe_var = tk.StringVar(value=CONTENT_TYPE_SOURCE_CODE)
        self.penjelasan_text = None
        self.analisa_text = None
        self.ai_frame = None
        self.img_frame = None
        self.langkah_container = None
        self.qa_container = None
        self.right_pane = None

        self.kode_items = []
        self.qa_items = []
        self.gambar_items = []
        self.kode_listbox = None
        self.gambar_listbox = None
        self.kode_container = None
        self.isi_a_text = None
        self.qa_tree = None
        self.qa_question_var = tk.StringVar()
        self.qa_answer_var = tk.StringVar()
        self.kode_title_var = tk.StringVar()
        self.gambar_caption_var = tk.StringVar()

        super().__init__(app, parent)

    def _build(self):
        self.pack_fill_expand()

        self._add_header(f"Daftar {self.section_name}", "Header.TLabel")

        ttk.Label(
            self,
            text="Prinsip IMK: alur sederhana, minim popup, dan feedback jelas di layar.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(0, 8))

        quick_add = ttk.LabelFrame(
            self,
            text=" Tambah Cepat Sub-Bab ",
            padding=10,
            style="Card.TLabelframe",
        )
        quick_add.pack(fill="x", pady=(0, 8))
        quick_add.columnconfigure(1, weight=1)

        ttk.Label(quick_add, text="Judul").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Entry(quick_add, textvariable=self.quick_title_var).grid(
            row=0, column=1, sticky="ew"
        )

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
        if self._supports_qa_content():
            ttk.Radiobutton(
                type_row,
                text=LABEL_Q_AND_A,
                variable=self.quick_type_var,
                value=CONTENT_TYPE_Q_AND_A,
            ).pack(side="left", padx=(10, 0))

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

        list_container = ttk.LabelFrame(
            self,
            text=" Ringkasan Sub-Bab ",
            padding=10,
            style="Card.TLabelframe",
        )
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

        scrollbar = ttk.Scrollbar(
            list_container,
            orient="vertical",
            command=self.main_tree.yview,
        )
        scrollbar.pack(side="right", fill="y")
        self.main_tree.configure(yscrollcommand=scrollbar.set)

        ttk.Label(self, textvariable=self.status_var, style="Muted.TLabel").pack(
            anchor="w",
            pady=(8, 0),
        )

        self._build_detail_editor()

    def _build_detail_editor(self):
        self.detail_frame = ttk.LabelFrame(
            self,
            text=" Editor Detail Sub-Bab ",
            padding=10,
            style="Card.TLabelframe",
        )

        header_row = ttk.Frame(self.detail_frame)
        header_row.pack(fill="x", pady=(0, 6))
        ttk.Label(header_row, text="Judul Sub-Bab", style="Subheader.TLabel").pack(
            anchor="w"
        )
        ttk.Entry(header_row, textvariable=self.detail_judul_var).pack(
            fill="x",
            pady=(2, 0),
        )

        desc_row = ttk.Frame(self.detail_frame)
        desc_row.pack(fill="x", pady=(2, 6))
        ttk.Label(desc_row, text="Penjelasan Singkat", style="Subheader.TLabel").pack(
            anchor="w"
        )
        self.penjelasan_text = tk.Text(
            desc_row,
            height=3,
            font=("Segoe UI", 10),
            relief="solid",
            borderwidth=1,
        )
        self.penjelasan_text.pack(fill="x", pady=(2, 0))

        type_row = ttk.Frame(self.detail_frame)
        type_row.pack(fill="x", pady=(0, 8))
        ttk.Label(type_row, text="Tipe Konten", style="Subheader.TLabel").pack(
            side="left",
            padx=(0, 8),
        )
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
        if self._supports_qa_content():
            ttk.Radiobutton(
                type_row,
                text=LABEL_Q_AND_A,
                variable=self.detail_tipe_var,
                value=CONTENT_TYPE_Q_AND_A,
            ).pack(side="left", padx=(10, 0))

        action_row = ttk.Frame(self.detail_frame)
        action_row.pack(fill="x", pady=(0, 10))

        ttk.Button(
            action_row,
            text="Generate Penjelasan AI",
            style="Action.TButton",
            command=self._run_penjelasan_ai_inline,
        ).pack(side="left")

        detail_split = ttk.Frame(self.detail_frame)
        detail_split.pack(fill="both", expand=True)

        left_pane = ttk.Frame(detail_split)
        left_pane.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right_pane = ttk.Frame(detail_split)
        right_pane.pack(side="right", fill="both", expand=True)
        self.right_pane = right_pane

        content_frame = ttk.LabelFrame(
            left_pane,
            text=" Isi Konten ",
            padding=10,
            style="Card.TLabelframe",
        )
        content_frame.pack(fill="both", expand=True)

        self.kode_container = ttk.Frame(content_frame)
        kode_main = ttk.Frame(self.kode_container)
        kode_main.pack(fill="both", expand=True)

        self.kode_listbox = tk.Listbox(kode_main, height=7, font=("Consolas", 10))
        self.kode_listbox.pack(side="left", fill="both", expand=True)
        self.kode_listbox.drop_target_register(DND_FILES)
        self.kode_listbox.dnd_bind("<<Drop>>", self._on_kode_drop)
        self.kode_listbox.bind("<<ListboxSelect>>", self._on_kode_select)

        k_btns = ttk.Frame(kode_main)
        k_btns.pack(side="right", padx=(5, 0))
        ttk.Button(k_btns, text="Tambah", command=self._add_kode).pack(
            fill="x",
            pady=(0, 4),
        )
        ttk.Button(k_btns, text="Hapus", command=self._remove_kode).pack(fill="x")

        kode_edit = ttk.Frame(self.kode_container)
        kode_edit.pack(fill="x", pady=(6, 0))
        ttk.Label(kode_edit, text="Judul File", style="Subheader.TLabel").pack(anchor="w")
        ttk.Entry(kode_edit, textvariable=self.kode_title_var).pack(fill="x", pady=(2, 4))
        ttk.Button(kode_edit, text="Update Judul", command=self._apply_kode_title).pack(
            anchor="e"
        )

        self.langkah_container = ttk.Frame(content_frame)
        self.isi_a_text = scrolledtext.ScrolledText(
            self.langkah_container,
            height=8,
            font=("Segoe UI", 10),
        )
        self.isi_a_text.pack(fill="both", expand=True)
        ttk.Button(
            self.langkah_container,
            text="Generate Langkah Kerja AI",
            style="Action.TButton",
            command=lambda: self._run_langkah_ai(self.detail_judul_var),
        ).pack(fill="x", pady=(5, 0))

        if self._supports_qa_content():
            self.qa_container = ttk.Frame(content_frame)

            qa_main = ttk.Frame(self.qa_container)
            qa_main.pack(fill="both", expand=True)

            self.qa_tree = ttk.Treeview(
                qa_main,
                columns=("pertanyaan", "jawaban"),
                show="headings",
                height=7,
            )
            self.qa_tree.heading("pertanyaan", text="Pertanyaan")
            self.qa_tree.heading("jawaban", text="Jawaban")
            self.qa_tree.column(
                "pertanyaan",
                width=320,
                minwidth=220,
                anchor="w",
                stretch=True,
            )
            self.qa_tree.column(
                "jawaban",
                width=420,
                minwidth=260,
                anchor="w",
                stretch=True,
            )
            self.qa_tree.pack(side="left", fill="both", expand=True)
            self.qa_tree.bind("<<TreeviewSelect>>", self._on_qa_select)

            qa_scroll = ttk.Scrollbar(qa_main, orient="vertical", command=self.qa_tree.yview)
            qa_scroll.pack(side="right", fill="y")
            self.qa_tree.configure(yscrollcommand=qa_scroll.set)

            qa_btns = ttk.Frame(self.qa_container)
            qa_btns.pack(fill="x", pady=(6, 0))
            ttk.Button(qa_btns, text="Tambah", command=self._add_qa_item).pack(side="left")
            ttk.Button(qa_btns, text="Perbarui", command=self._update_qa_item).pack(
                side="left",
                padx=(6, 0),
            )
            ttk.Button(qa_btns, text="Hapus", command=self._remove_qa_item).pack(
                side="left",
                padx=(6, 0),
            )
            ttk.Button(
                qa_btns,
                text="Jawab AI",
                style="Action.TButton",
                command=self._generate_qa_answer,
            ).pack(side="right")

            qa_fields = ttk.Frame(self.qa_container)
            qa_fields.pack(fill="x", pady=(8, 0))
            ttk.Label(qa_fields, text="Pertanyaan", style="Subheader.TLabel").pack(anchor="w")
            ttk.Entry(qa_fields, textvariable=self.qa_question_var).pack(
                fill="x",
                pady=(2, 6),
            )
            ttk.Label(qa_fields, text="Jawaban", style="Subheader.TLabel").pack(anchor="w")
            ttk.Entry(qa_fields, textvariable=self.qa_answer_var).pack(fill="x", pady=(2, 4))

            self.qa_container.pack_forget()

        img_frame = ttk.LabelFrame(
            left_pane,
            text=" Lampiran Gambar ",
            padding=10,
            style="Card.TLabelframe",
        )
        self.img_frame = img_frame
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
        ttk.Button(g_btns, text="Tambah", command=self._add_gambar).pack(
            fill="x",
            pady=(0, 4),
        )
        ttk.Button(g_btns, text="Screenshot", command=self._capture_gambar).pack(
            fill="x",
            pady=(0, 4),
        )
        ttk.Button(g_btns, text="Hapus", command=self._remove_gambar).pack(fill="x")

        gambar_edit = ttk.Frame(img_frame)
        gambar_edit.pack(fill="x", pady=(6, 0))
        ttk.Label(gambar_edit, text="Caption", style="Subheader.TLabel").pack(anchor="w")
        ttk.Entry(gambar_edit, textvariable=self.gambar_caption_var).pack(
            fill="x",
            pady=(2, 4),
        )
        ttk.Button(
            gambar_edit,
            text="Update Caption",
            command=self._apply_gambar_caption,
        ).pack(anchor="e")

        ai_frame = ttk.LabelFrame(
            right_pane,
            text=" Hasil Analisa (AI) ",
            padding=10,
            style="Card.TLabelframe",
        )
        self.ai_frame = ai_frame
        ai_frame.pack(fill="both", expand=True)
        self.analisa_text = scrolledtext.ScrolledText(
            ai_frame,
            font=("Segoe UI", 10),
            bg="#ffffff",
        )
        self.analisa_text.pack(fill="both", expand=True, pady=(0, 10))

        ttk.Button(
            ai_frame,
            text="Jalankan Analisa AI",
            style="Action.TButton",
            command=self._run_analisa_ai_inline,
        ).pack(fill="x")

        footer = ttk.Frame(self.detail_frame)
        footer.pack(fill="x", pady=(10, 0))
        ttk.Button(footer, text="Tutup Editor", command=self._cancel_inline_edit).pack(
            side="right"
        )
        ttk.Button(
            footer,
            text="Simpan Perubahan",
            style="Action.TButton",
            command=self._save_inline_edit,
        ).pack(side="right", padx=(0, 6))

        self.detail_tipe_var.trace_add("write", lambda *_: self._toggle_detail_content())
