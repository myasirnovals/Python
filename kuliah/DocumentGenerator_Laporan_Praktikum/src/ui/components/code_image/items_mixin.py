"""Item lifecycle mixin for code-image tab."""

import tkinter as tk

from ui.constants import (
    CONTENT_TYPE_Q_AND_A,
    CONTENT_TYPE_SOURCE_CODE,
    CONTENT_TYPE_WORK_STEPS,
    LABEL_Q_AND_A,
    LABEL_SOURCE_CODE,
    LABEL_WORK_STEPS,
)
from ui.utils import UIUtils


class CodeImageItemsMixin:
    """Handle CRUD state and inline editor lifecycle for section items."""

    def get_items(self):
        return self.items

    def fill_test_data(self):
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
        if self.main_tree is None:
            return
        for child in self.main_tree.get_children():
            self.main_tree.delete(child)

        for i, item in enumerate(self.items, 1):
            judul = item.get("judul_sub_bab") or f"Sub-Bab {i}"
            tipe = self._get_type_label(item.get("tipe"))
            kode_count = len(item.get("list_kode") or [])
            gambar_count = len(item.get("list_gambar") or [])
            self.main_tree.insert(
                "",
                "end",
                iid=str(i - 1),
                values=(judul, tipe, str(kode_count), str(gambar_count)),
            )

    def _add_item(self):
        title = self.quick_title_var.get().strip()
        if not title:
            self.status_var.set("Judul sub-bab wajib diisi sebelum menambahkan.")
            return

        tipe = self.quick_type_var.get() or CONTENT_TYPE_SOURCE_CODE
        label_a = self._get_type_label(tipe)
        self.items.append(
            {
                "judul_sub_bab": title,
                "penjelasan_singkat": "",
                "tipe": tipe,
                "label_point_a": label_a,
                "list_kode": [],
                "isi_a": "",
                "langkah_list": [],
                "qa_items": [],
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
        self.status_var.set(
            "Sub-bab berhasil ditambahkan. Pilih Edit Detail untuk melengkapi isi."
        )
        self._start_inline_edit(last_index)

    def _edit_item(self):
        index = self._selected_main_index()
        if index is None:
            self.status_var.set("Pilih satu sub-bab terlebih dahulu untuk diedit.")
            return
        self._start_inline_edit(index)

    def _remove_item(self):
        index = self._selected_main_index()
        if index is None:
            self.status_var.set("Pilih satu sub-bab terlebih dahulu untuk dihapus.")
            return
        del self.items[index]
        self._refresh_list()
        self.status_var.set("Sub-bab dihapus.")
        if self.current_edit_index is not None and self.current_edit_index == index:
            self._cancel_inline_edit()

    def _selected_main_index(self):
        if self.main_tree is None:
            return None
        selected = self.main_tree.selection()
        if not selected:
            return None
        try:
            return int(selected[0])
        except (ValueError, TypeError):
            return None

    def _start_inline_edit(self, index):
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
                        teks = (
                            l_item.get("langkah_kerja", "").strip()
                            if isinstance(l_item, dict)
                            else str(l_item).strip()
                        )
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
        self.qa_items = [
            dict(qa) for qa in (item.get("qa_items") or item.get("qa_list") or [])
        ]
        self.gambar_items = [dict(g) for g in (item.get("list_gambar") or [])]
        self._refresh_dialog_lists()
        self._refresh_qa_list()
        self.kode_title_var.set("")
        self.gambar_caption_var.set("")
        self.qa_question_var.set("")
        self.qa_answer_var.set("")

        self._toggle_detail_content()
        self.detail_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.status_var.set("Mode edit aktif. Ubah data lalu klik Simpan Perubahan.")

    def _save_inline_edit(self):
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
        label_a = self._get_type_label(tipe)
        langkah_list = (
            UIUtils.parse_step_list(self.isi_a_text.get("1.0", "end-1c"))
            if self.isi_a_text is not None
            else []
        )
        isi_a_value = (
            self._serialize_qa_items()
            if tipe == CONTENT_TYPE_Q_AND_A
            else (
                self.isi_a_text.get("1.0", "end-1c")
                if self.isi_a_text is not None
                else ""
            )
        )

        self.items[self.current_edit_index] = {
            "judul_sub_bab": judul,
            "penjelasan_singkat": (
                self.penjelasan_text.get("1.0", "end-1c")
                if self.penjelasan_text
                else ""
            ),
            "tipe": tipe,
            "label_point_a": label_a,
            "list_kode": self.kode_items,
            "isi_a": isi_a_value,
            "langkah_list": langkah_list,
            "qa_items": self.qa_items,
            "list_gambar": self.gambar_items,
            "isi_analisa": (
                self.analisa_text.get("1.0", "end-1c") if self.analisa_text else ""
            ),
        }

        idx = self.current_edit_index
        self._refresh_list()
        if self.main_tree is not None:
            self.main_tree.selection_set(str(idx))
            self.main_tree.focus(str(idx))
            self.main_tree.see(str(idx))
        self.status_var.set("Perubahan sub-bab berhasil disimpan.")

    def _cancel_inline_edit(self):
        self.current_edit_index = None
        if self.detail_frame is not None:
            self.detail_frame.pack_forget()
        self.status_var.set("Editor detail ditutup.")

    def _toggle_detail_content(self):
        if self.kode_container is None or self.langkah_container is None:
            return

        self.kode_container.pack_forget()
        self.langkah_container.pack_forget()
        if self.qa_container is not None:
            self.qa_container.pack_forget()
        if self.ai_frame is not None:
            self.ai_frame.pack_forget()
        if self.img_frame is not None:
            self.img_frame.pack_forget()
        if self.right_pane is not None:
            self.right_pane.pack_forget()

        if self.detail_tipe_var.get() == CONTENT_TYPE_SOURCE_CODE:
            if self.right_pane is not None:
                self.right_pane.pack(side="right", fill="both", expand=True)
            self.kode_container.pack(fill="both", expand=True)
            if self.img_frame is not None:
                self.img_frame.pack(fill="x", pady=(10, 0))
            if self.ai_frame is not None:
                self.ai_frame.pack(fill="both", expand=True)
        elif (
            self.detail_tipe_var.get() == CONTENT_TYPE_Q_AND_A
            and self.qa_container is not None
        ):
            self.qa_container.pack(fill="both", expand=True)
        else:
            if self.right_pane is not None:
                self.right_pane.pack(side="right", fill="both", expand=True)
            self.langkah_container.pack(fill="both", expand=True)
            if self.img_frame is not None:
                self.img_frame.pack(fill="x", pady=(10, 0))
            if self.ai_frame is not None:
                self.ai_frame.pack(fill="both", expand=True)

    def _get_type_label(self, tipe_value):
        if tipe_value == CONTENT_TYPE_SOURCE_CODE:
            return LABEL_SOURCE_CODE
        if tipe_value == CONTENT_TYPE_Q_AND_A:
            return LABEL_Q_AND_A
        return LABEL_WORK_STEPS
