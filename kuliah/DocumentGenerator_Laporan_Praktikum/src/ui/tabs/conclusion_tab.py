"""Conclusion tab (OOP tab layer)."""

import tkinter as tk
from tkinter import ttk, scrolledtext

from ui.core.base_tab import BaseTab


class ConclusionTab(BaseTab):
    def __init__(self, app, parent):
        self.kesimpulan_text = None
        super().__init__(app, parent)

    def _build(self):
        self.pack_fill_expand()
        self._add_header("Kesimpulan Laporan", "Header.TLabel")

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 10))
        ttk.Button(
            toolbar,
            text="✨ Generate Kesimpulan (AI)",
            style="Action.TButton",
            command=self._run_kesimpulan_ai,
        ).pack(side="left")

        ttk.Label(
            self,
            text="Anda dapat mengedit kesimpulan secara manual di bawah ini:",
            foreground="#666666",
        ).pack(anchor="w", pady=(5, 5))

        self.kesimpulan_text = scrolledtext.ScrolledText(
            self,
            wrap="word",
            height=16,
            font=("Segoe UI", 11),
            padx=10,
            pady=10,
        )
        self.kesimpulan_text.pack(fill="both", expand=True)

    def _run_kesimpulan_ai(self):
        data_bab1 = self.app.results_tab.get_items()
        data_bab2 = self.app.tasks_tab.get_items()

        if not data_bab1 and not data_bab2:
            self.show_warning(
                "Data Kosong",
                "Daftar Hasil Praktikum (Bab 1) atau Tugas (Bab 2) belum diisi. AI membutuhkan data tersebut untuk membuat kesimpulan.",
            )
            return

        res, err = self.app.analysis_service.generate_conclusion(data_bab1, data_bab2)
        if err:
            self.show_error("AI Error", err)
            return

        self.kesimpulan_text.delete("1.0", tk.END)
        self.kesimpulan_text.insert("1.0", res)

    def get_kesimpulan(self) -> str:
        if not self.kesimpulan_text:
            return ""
        return self.kesimpulan_text.get("1.0", "end-1c")

    def fill_test_data(self):
        if not self.kesimpulan_text:
            return
        self.kesimpulan_text.delete("1.0", tk.END)
        self.kesimpulan_text.insert(
            "1.0",
            "Praktikum ini menunjukkan pentingnya validasi input dan kontrol alur program. "
            "Penggunaan percabangan membantu memastikan hasil sesuai kondisi yang ditetapkan. "
            "Secara keseluruhan, implementasi berjalan sesuai spesifikasi dan dapat dikembangkan lebih lanjut.",
        )
