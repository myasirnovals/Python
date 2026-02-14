from tkinter import filedialog, messagebox, ttk


class GenerateTab(ttk.Frame):
    def __init__(self, app, parent):
        super().__init__(parent, padding=40)
        self.app = app
        self._build()

    def _build(self):
        self.pack(fill="both", expand=True)

        center_frame = ttk.Frame(self)
        center_frame.place(relx=0.5, rely=0.4, anchor="center")

        ttk.Label(
            center_frame, text="Laporan Anda Sudah Siap!", font=("Segoe UI", 16, "bold")
        ).pack(pady=10)

        ttk.Label(
            center_frame,
            text="Pastikan semua data di tab sebelumnya sudah diisi dengan benar.",
            foreground="#666666",
        ).pack(pady=(0, 30))

        gen_btn = ttk.Button(
            center_frame,
            text="🚀 GENERATE LAPORAN (.DOCX)",
            style="Action.TButton",
            command=self._generate,
        )
        gen_btn.pack(ipadx=20, ipady=10)

        ttk.Label(
            center_frame,
            text="File akan disimpan secara otomatis setelah Anda memilih lokasi penyimpanan.",
            font=("Segoe UI", 8),
            foreground="#999999",
        ).pack(pady=20)

    def _generate(self):
        cover = self.app.cover_tab.get_cover_data()

        required = ["mata_kuliah", "nomor_modul", "judul", "nama", "nim", "tahun"]
        if any(not cover[k] for k in required):
            messagebox.showwarning("Validasi", "Data cover belum lengkap.")
            return

        cover["mata_kuliah"] = cover["mata_kuliah"].upper()
        cover["judul"] = cover["judul"].upper()
        cover["nama"] = cover["nama"].upper()

        kesimpulan = self.app.bab3_tab.get_kesimpulan()
        if not kesimpulan.strip():
            messagebox.showwarning("Validasi", "Kesimpulan belum diisi.")
            return

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

        try:
            self.app.report_service.render_report(
                self.app.cover_tab.get_template_choice(),
                cover,
                self.app.bab1_tab.get_items(),
                self.app.bab2_tab.get_items(),
                kesimpulan,
                output_path,
            )
            messagebox.showinfo("Sukses", f"Laporan tersimpan di:\n{output_path}")
        except FileNotFoundError as e:
            messagebox.showerror(
                "Template Tidak Ada",
                f"File template '{e.args[0]}' tidak ditemukan.",
            )
        except Exception as e:
            messagebox.showerror("Gagal", f"Gagal render: {e}")