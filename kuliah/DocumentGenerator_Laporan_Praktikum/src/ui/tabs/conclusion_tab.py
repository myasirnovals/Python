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
            text="Draf kesimpulan terdiri dari 3 paragraf (3-5 kalimat per paragraf):",
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

        cover_data = self.app.cover_tab.get_cover_data()
        modul_text = self.app.cover_tab.get_modul_text()
        modul_path = self.app.cover_tab.get_modul_path()

        res, err = self.app.analysis_service.generate_conclusion(
            data_bab1,
            data_bab2,
            cover_data=cover_data,
            modul_text=modul_text,
            modul_path=modul_path,
        )
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
            "Pada praktikum kali ini, implementasi pengolahan sinyal suara dan ekstraksi parameter audio telah diselesaikan sesuai target teknis modul. "
            "Pengujian fungsi filter dan transformasi domain waktu ke domain frekuensi menghasilkan representasi data yang akurat. "
            "Praktikan berhasil memverifikasi karakteristik spektrum suara secara langsung melalui visualisasi grafik yang terbentuk.\n\n"
            "Analisis teknis menunjukkan bahwa penyesuaian parameter sampling rate dan frame size berpengaruh langsung terhadap resolusi sinyal yang diamati. "
            "Hasil eksekusi program mengonfirmasi keselarasan antara prinsip teoritis modul dengan data pengujian nyata di laboratorium. "
            "Keluaran keluaran numerik dan spektral membuktikan stabilitas algoritma pemrosesan yang digunakan.\n\n"
            "Secara konseptual, praktikum ini memperkuat pemahaman mengenai alur kerja digital signal processing untuk kebutuhan speech recognition. "
            "Metode analisis yang diterapkan terbukti efektif dalam membedakan fitur unik pada masing-masing sampel audio. "
            "Keterampilan teknis yang diperoleh menjadi fondasi esensial untuk pengembangan sistem pemrosesan suara pada tahap lanjut.",
        )
