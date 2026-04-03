"""generate_tab.py - Report generation and export."""

from tkinter import filedialog, ttk

from ui.base import BaseTab


class GenerateTab(BaseTab):
    """
    Tab for generating and exporting final lab report.
    
    Validates all inputs from previous tabs and renders the compiled report as .docx file.
    """
    
    def __init__(self, app, parent):
        super().__init__(app, parent)
    
    def _build(self):
        self.pack(fill="both", expand=True)

        card = ttk.LabelFrame(self, text=" Finalisasi Laporan ", padding=22, style="Card.TLabelframe")
        card.place(relx=0.5, rely=0.45, anchor="center")

        center_frame = ttk.Frame(card)
        center_frame.pack(fill="both", expand=True)
        
        ttk.Label(
            center_frame, text="Laporan Anda Sudah Siap!", font=("Segoe UI", 16, "bold")
        ).pack(pady=10)
        
        ttk.Label(
            center_frame,
            text="Pastikan semua data di tab sebelumnya sudah diisi dengan benar.",
            foreground="#666666",
        ).pack(pady=(0, 30))
        
        ttk.Button(
            center_frame,
            text="Generate Laporan (.DOCX)",
            style="Action.TButton",
            command=self._generate,
        ).pack(ipadx=20, ipady=10)
        
        ttk.Label(
            center_frame,
            text="File akan disimpan secara otomatis setelah Anda memilih lokasi penyimpanan.",
            font=("Segoe UI", 8),
            foreground="#999999",
        ).pack(pady=20)
    
    def _generate(self):
        """Generate and save the final report."""
        # Get cover data
        cover = self.app.cover_tab.get_cover_data()
        
        # Validate cover data
        required = ["mata_kuliah", "nomor_modul", "judul", "nama", "nim", "tahun"]
        if any(not cover[k] for k in required):
            self.show_warning("Validasi", "Data cover belum lengkap.")
            return
        
        # Normalize cover data
        cover["mata_kuliah"] = cover["mata_kuliah"].upper()
        cover["judul"] = cover["judul"].upper()
        cover["nama"] = cover["nama"].upper()
        
        # Get conclusion
        kesimpulan = self.app.conclusion_tab.get_kesimpulan()
        if not kesimpulan.strip():
            self.show_warning("Validasi", "Kesimpulan belum diisi.")
            return
        
        # Ask for save location
        output_name = (
            f"Laporan_Modul_{cover['nomor_modul']}_{cover['nama'].replace(' ', '_')}.docx"
        )
        output_path = filedialog.asksaveasfilename(
            title="Simpan Laporan",
            defaultextension=".docx",
            initialfile=output_name,
            filetypes=[("Word Document", "*.docx")],
        )
        if not output_path:
            return
        
        # Generate report
        try:
            self.app.report_service.render_report(
                self.app.cover_tab.get_template_choice(),
                cover,
                self.app.results_tab.get_items(),
                self.app.tasks_tab.get_items(),
                kesimpulan,
                output_path,
            )
            self.show_info("Sukses", f"Laporan tersimpan di:\n{output_path}")
        except FileNotFoundError as e:
            self.show_error(
                "Template Tidak Ada",
                f"File template '{e.args[0]}' tidak ditemukan.",
            )
        except Exception as e:
            self.show_error("Gagal", f"Gagal render: {e}")