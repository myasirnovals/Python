"""AI action mixin for code-image tab."""

import tkinter as tk
from tkinter import filedialog

from ui.constants import CONTENT_TYPE_Q_AND_A


class CodeImageAIMixin:
    """Provide AI-powered helper actions used by detail editor."""

    def _run_penjelasan_ai_inline(self):
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
            return

        self.penjelasan_text.delete("1.0", tk.END)
        self.penjelasan_text.insert("1.0", res)
        self.status_var.set("Penjelasan singkat berhasil digenerate.")

    def _run_analisa_ai_inline(self):
        isi_a_value = (
            self._serialize_qa_items()
            if self.detail_tipe_var.get() == CONTENT_TYPE_Q_AND_A
            else self.isi_a_text.get("1.0", tk.END)
        )
        res, err = self.app.analysis_service.generate_analysis(
            self.detail_tipe_var.get(),
            isi_a_value,
            self.kode_items,
            self.gambar_items,
            self.app.cover_tab.get_template_choice(),
        )
        if err:
            self.show_error("AI Error", err)
            return

        self.analisa_text.delete("1.0", tk.END)
        self.analisa_text.insert("1.0", res)
        self.status_var.set("Analisa AI berhasil diperbarui.")

    def _run_langkah_ai(self, judul_var):
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
            return

        self.isi_a_text.delete("1.0", tk.END)
        self.isi_a_text.insert("1.0", res)
