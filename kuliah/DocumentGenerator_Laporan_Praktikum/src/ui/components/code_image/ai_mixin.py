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

        cover_data = self.app.cover_tab.get_cover_data()
        modul_path = self.app.cover_tab.get_modul_path()

        res, err = self.app.analysis_service.generate_penjelasan_singkat(
            judul_sub=judul,
            modul_text=modul_text,
            cover_data=cover_data,
            modul_path=modul_path,
        )
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
        judul = self.detail_judul_var.get().strip()
        modul_text = self.app.cover_tab.get_modul_text()
        cover_data = self.app.cover_tab.get_cover_data()
        modul_path = self.app.cover_tab.get_modul_path()

        res, err = self.app.analysis_service.generate_analysis(
            tipe=self.detail_tipe_var.get(),
            isi_a_text=isi_a_value,
            kode_items=self.kode_items,
            gambar_items=self.gambar_items,
            template_choice=self.app.cover_tab.get_template_choice(),
            judul_sub=judul,
            modul_text=modul_text,
            cover_data=cover_data,
            modul_path=modul_path,
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
        cover_data = self.app.cover_tab.get_cover_data()
        modul_path = self.app.cover_tab.get_modul_path()
        isi_deskripsi = (
            self.isi_a_text.get("1.0", tk.END).strip()
            if hasattr(self, "isi_a_text")
            else ""
        )
        image_path = (
            self.gambar_items[0]["path"]
            if (self.gambar_items and "path" in self.gambar_items[0])
            else None
        )

        if not modul_text and not image_path:
            image_path = filedialog.askopenfilename(
                title="Pilih Screenshot",
                filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")],
            )

        res, err = self.app.analysis_service.generate_langkah_kerja(
            judul_sub=judul,
            modul_text=modul_text,
            image_path=image_path,
            cover_data=cover_data,
            modul_path=modul_path,
            isi_deskripsi=isi_deskripsi,
        )
        if err:
            self.show_error("AI Error", err)
            return

        self.isi_a_text.delete("1.0", tk.END)
        self.isi_a_text.insert("1.0", res)
