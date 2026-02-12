# Lab Report Generator - creates formatted practicum reports from user input.
# Copyright (C) 2026 Muhamad Yasir Noval
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact: myasirnoval23@if.unjani.ac.id

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext

from docxtpl import DocxTemplate

from app.ai_client import GeminiClient
from app.doc_helpers import muat_gambar
from app.prompts import build_prompt, instruksi_gaya

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lab Report Generator")
        self.geometry("980x720")

        self.ai_client = GeminiClient()
        self.ai_ready = False

        self.cover_vars = {
            "mata_kuliah": tk.StringVar(),
            "nomor_modul": tk.StringVar(),
            "judul": tk.StringVar(),
            "nama": tk.StringVar(),
            "nim": tk.StringVar(),
            "tahun": tk.StringVar(),
        }
        self.template_choice = tk.StringVar(value="1")

        self.bab1_items = []
        self.bab2_items = []
        self.kesimpulan_text = None

        self._build_ui()

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        cover_tab = ttk.Frame(notebook)
        bab1_tab = ttk.Frame(notebook)
        bab2_tab = ttk.Frame(notebook)
        bab3_tab = ttk.Frame(notebook)
        generate_tab = ttk.Frame(notebook)

        notebook.add(cover_tab, text="Cover")
        notebook.add(bab1_tab, text="Bab 1")
        notebook.add(bab2_tab, text="Bab 2")
        notebook.add(bab3_tab, text="Bab 3")
        notebook.add(generate_tab, text="Generate")

        self._build_cover_tab(cover_tab)
        self._build_bab1_tab(bab1_tab)
        self._build_bab2_tab(bab2_tab)
        self._build_bab3_tab(bab3_tab)
        self._build_generate_tab(generate_tab)

    def _build_cover_tab(self, parent):
        frame = ttk.Frame(parent, padding=12)
        frame.pack(fill="both", expand=True)

        row = 0
        for label, key in [
            ("Mata Kuliah", "mata_kuliah"),
            ("Nomor Modul", "nomor_modul"),
            ("Judul Modul", "judul"),
            ("Nama", "nama"),
            ("NIM", "nim"),
            ("Tahun", "tahun"),
        ]:
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=6)
            ttk.Entry(frame, textvariable=self.cover_vars[key], width=48).grid(
                row=row, column=1, sticky="w", pady=6
            )
            row += 1

        ttk.Label(frame, text="Gaya Format").grid(row=row, column=0, sticky="w", pady=8)
        options = ttk.Frame(frame)
        options.grid(row=row, column=1, sticky="w", pady=8)
        ttk.Radiobutton(
            options,
            text="Gaya Rapat (format-1.docx)",
            variable=self.template_choice,
            value="1",
        ).pack(anchor="w")
        ttk.Radiobutton(
            options,
            text="Gaya Renggang (format-2.docx)",
            variable=self.template_choice,
            value="2",
        ).pack(anchor="w")

    def _build_bab1_tab(self, parent):
        frame = ttk.Frame(parent, padding=12)
        frame.pack(fill="both", expand=True)

        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="Tambah Sub-Bab", command=self._add_bab1).pack(
            side="left", padx=4
        )
        ttk.Button(toolbar, text="Edit", command=self._edit_bab1).pack(
            side="left", padx=4
        )
        ttk.Button(toolbar, text="Hapus", command=self._remove_bab1).pack(
            side="left", padx=4
        )

        self.bab1_listbox = tk.Listbox(frame, height=18)
        self.bab1_listbox.pack(fill="both", expand=True, pady=10)

    def _build_bab2_tab(self, parent):
        frame = ttk.Frame(parent, padding=12)
        frame.pack(fill="both", expand=True)

        toolbar = ttk.Frame(frame)
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="Tambah Tugas", command=self._add_bab2).pack(
            side="left", padx=4
        )
        ttk.Button(toolbar, text="Edit", command=self._edit_bab2).pack(
            side="left", padx=4
        )
        ttk.Button(toolbar, text="Hapus", command=self._remove_bab2).pack(
            side="left", padx=4
        )

        self.bab2_listbox = tk.Listbox(frame, height=18)
        self.bab2_listbox.pack(fill="both", expand=True, pady=10)

    def _build_bab3_tab(self, parent):
        frame = ttk.Frame(parent, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Kesimpulan").pack(anchor="w")
        self.kesimpulan_text = scrolledtext.ScrolledText(frame, wrap="word", height=16)
        self.kesimpulan_text.pack(fill="both", expand=True, pady=8)

    def _build_generate_tab(self, parent):
        frame = ttk.Frame(parent, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Klik Generate untuk membuat file laporan .docx",
        ).pack(anchor="w", pady=6)

        ttk.Button(frame, text="Generate Report", command=self._generate).pack(
            anchor="w", pady=10
        )

    def _refresh_bab1_list(self):
        self.bab1_listbox.delete(0, tk.END)
        for i, item in enumerate(self.bab1_items, 1):
            judul = item.get("judul_sub_bab") or f"Sub-Bab {i}"
            tipe = "Source Code" if item.get("tipe") == "1" else "Langkah Kerja"
            self.bab1_listbox.insert(tk.END, f"{i}. {judul} [{tipe}]")

    def _refresh_bab2_list(self):
        self.bab2_listbox.delete(0, tk.END)
        for i, item in enumerate(self.bab2_items, 1):
            judul = item.get("judul_sub_bab") or f"Tugas {i}"
            self.bab2_listbox.insert(tk.END, f"{i}. {judul}")

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

    def _add_bab2(self):
        data = self._open_bab2_dialog()
        if data:
            self.bab2_items.append(data)
            self._refresh_bab2_list()

    def _edit_bab2(self):
        sel = self.bab2_listbox.curselection()
        if not sel:
            return
        index = sel[0]
        data = self._open_bab2_dialog(self.bab2_items[index])
        if data:
            self.bab2_items[index] = data
            self._refresh_bab2_list()

    def _remove_bab2(self):
        sel = self.bab2_listbox.curselection()
        if not sel:
            return
        index = sel[0]
        del self.bab2_items[index]
        self._refresh_bab2_list()

    def _open_bab1_dialog(self, initial=None):
        dialog = tk.Toplevel(self)
        dialog.title("Sub-Bab 1")
        dialog.geometry("820x720")
        dialog.transient(self)
        dialog.grab_set()

        data = initial.copy() if initial else {}
        tipe_var = tk.StringVar(value=data.get("tipe", "1"))

        judul_var = tk.StringVar(value=data.get("judul_sub_bab", ""))
        ttk.Label(dialog, text="Judul Sub-Bab").pack(anchor="w", padx=12, pady=6)
        judul_entry = ttk.Entry(dialog, textvariable=judul_var, width=60)
        judul_entry.pack(anchor="w", padx=12)

        tipe_frame = ttk.Frame(dialog)
        tipe_frame.pack(anchor="w", padx=12, pady=8)
        ttk.Label(tipe_frame, text="Tipe Point A").pack(side="left")
        ttk.Radiobutton(
            tipe_frame, text="Source Code", variable=tipe_var, value="1"
        ).pack(side="left", padx=8)
        ttk.Radiobutton(
            tipe_frame, text="Langkah Kerja", variable=tipe_var, value="2"
        ).pack(side="left", padx=8)

        isi_frame = ttk.Frame(dialog)
        isi_frame.pack(fill="both", expand=False, padx=12, pady=8)
        isi_label = ttk.Label(isi_frame, text="Isi Langkah Kerja")
        isi_label.pack(anchor="w")
        isi_text = scrolledtext.ScrolledText(isi_frame, height=6, wrap="word")
        isi_text.pack(fill="both", expand=True)
        if data.get("isi_a"):
            isi_text.insert("1.0", data.get("isi_a"))

        kode_frame = ttk.LabelFrame(dialog, text="Source Code")
        kode_frame.pack(fill="both", expand=False, padx=12, pady=8)

        kode_list = tk.Listbox(kode_frame, height=5)
        kode_list.pack(fill="both", expand=True, padx=6, pady=6)

        kode_items = data.get("kode_files", [])

        def refresh_kode_list():
            kode_list.delete(0, tk.END)
            for i, item in enumerate(kode_items, 1):
                name = item.get("nama") or f"File {i}"
                kode_list.insert(tk.END, f"{i}. {name}")

        def add_kode():
            result = self._open_kode_dialog()
            if result:
                kode_items.append(result)
                refresh_kode_list()

        def edit_kode():
            sel = kode_list.curselection()
            if not sel:
                return
            idx = sel[0]
            result = self._open_kode_dialog(kode_items[idx])
            if result:
                kode_items[idx] = result
                refresh_kode_list()

        def remove_kode():
            sel = kode_list.curselection()
            if not sel:
                return
            idx = sel[0]
            del kode_items[idx]
            refresh_kode_list()

        toolbar = ttk.Frame(kode_frame)
        toolbar.pack(fill="x", padx=6, pady=4)
        ttk.Button(toolbar, text="Tambah File", command=add_kode).pack(side="left")
        ttk.Button(toolbar, text="Edit", command=edit_kode).pack(side="left", padx=6)
        ttk.Button(toolbar, text="Hapus", command=remove_kode).pack(side="left")

        refresh_kode_list()

        gambar_frame = ttk.LabelFrame(dialog, text="Gambar")
        gambar_frame.pack(fill="both", expand=False, padx=12, pady=8)

        gambar_list = tk.Listbox(gambar_frame, height=5)
        gambar_list.pack(fill="both", expand=True, padx=6, pady=6)
        gambar_items = data.get("gambar_paths", [])

        def refresh_gambar_list():
            gambar_list.delete(0, tk.END)
            for i, item in enumerate(gambar_items, 1):
                name = os.path.basename(item.get("path", ""))
                caption = item.get("caption", "")
                gambar_list.insert(tk.END, f"{i}. {name} - {caption}")

        def add_gambar():
            path = filedialog.askopenfilename(
                title="Pilih Gambar",
                filetypes=[("Image", "*.png;*.jpg;*.jpeg;*.bmp")],
            )
            if not path:
                return
            caption = self._prompt_caption()
            if caption is None:
                return
            gambar_items.append({"path": path, "caption": caption})
            refresh_gambar_list()

        def remove_gambar():
            sel = gambar_list.curselection()
            if not sel:
                return
            idx = sel[0]
            del gambar_items[idx]
            refresh_gambar_list()

        g_toolbar = ttk.Frame(gambar_frame)
        g_toolbar.pack(fill="x", padx=6, pady=4)
        ttk.Button(g_toolbar, text="Tambah Gambar", command=add_gambar).pack(
            side="left"
        )
        ttk.Button(g_toolbar, text="Hapus", command=remove_gambar).pack(
            side="left", padx=6
        )

        refresh_gambar_list()

        analisa_frame = ttk.LabelFrame(dialog, text="Analisa")
        analisa_frame.pack(fill="both", expand=True, padx=12, pady=8)
        analisa_text = scrolledtext.ScrolledText(analisa_frame, height=8, wrap="word")
        analisa_text.pack(fill="both", expand=True, padx=6, pady=6)
        if data.get("analisa"):
            analisa_text.insert("1.0", data.get("analisa"))

        def generate_ai():
            if not self.ai_ready:
                if not self.ai_client.get_active_model():
                    messagebox.showerror(
                        "AI Error", "AI tidak bisa connect. Periksa API key."
                    )
                    return
                self.ai_ready = True

            isi_a = isi_text.get("1.0", "end-1c")
            if tipe_var.get() == "1":
                isi_a = self._concat_kode_for_prompt(kode_items)

            prompt = build_prompt(tipe_var.get(), isi_a, instruksi_gaya())
            image_path = gambar_items[0]["path"] if gambar_items else None
            result = self.ai_client.ask(prompt, image_path)

            if self.template_choice.get() == "1" and result:
                result = result.replace("\n\n", "\n")
                result = "\t" + result.replace("\n", "\n\t")

            analisa_text.delete("1.0", tk.END)
            analisa_text.insert("1.0", result)

        ai_btn = ttk.Button(analisa_frame, text="Generate AI", command=generate_ai)
        ai_btn.pack(anchor="w", padx=6, pady=4)

        def update_visibility(*_):
            if tipe_var.get() == "2":
                isi_frame.pack(fill="both", expand=False, padx=12, pady=8)
                kode_frame.pack_forget()
            else:
                isi_frame.pack_forget()
                kode_frame.pack(fill="both", expand=False, padx=12, pady=8)

        tipe_var.trace_add("write", update_visibility)
        update_visibility()

        result = {"value": None}

        def on_save():
            judul = judul_var.get().strip()
            if not judul:
                messagebox.showwarning("Validasi", "Judul sub-bab belum diisi.")
                return

            isi_a_value = isi_text.get("1.0", "end-1c") if tipe_var.get() == "2" else ""
            if tipe_var.get() == "2" and not isi_a_value.strip():
                messagebox.showwarning("Validasi", "Langkah kerja belum diisi.")
                return

            if tipe_var.get() == "1" and len(kode_items) == 0:
                messagebox.showwarning("Validasi", "Minimal satu file kode diperlukan.")
                return

            result["value"] = {
                "judul_sub_bab": judul,
                "tipe": tipe_var.get(),
                "isi_a": isi_a_value,
                "kode_files": kode_items,
                "gambar_paths": gambar_items,
                "analisa": analisa_text.get("1.0", "end-1c"),
            }
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        action_frame = ttk.Frame(dialog)
        action_frame.pack(fill="x", padx=12, pady=10)
        ttk.Button(action_frame, text="Simpan", command=on_save).pack(
            side="right", padx=6
        )
        ttk.Button(action_frame, text="Batal", command=on_cancel).pack(side="right")

        self.wait_window(dialog)
        return result["value"]

    def _open_bab2_dialog(self, initial=None):
        dialog = tk.Toplevel(self)
        dialog.title("Tugas Praktikum")
        dialog.geometry("760x640")
        dialog.transient(self)
        dialog.grab_set()

        data = initial.copy() if initial else {}

        judul_var = tk.StringVar(value=data.get("judul_sub_bab", ""))
        ttk.Label(dialog, text="Topik Tugas").pack(anchor="w", padx=12, pady=6)
        judul_entry = ttk.Entry(dialog, textvariable=judul_var, width=60)
        judul_entry.pack(anchor="w", padx=12)

        ttk.Label(dialog, text="Soal").pack(anchor="w", padx=12, pady=6)
        soal_text = scrolledtext.ScrolledText(dialog, height=6, wrap="word")
        soal_text.pack(fill="both", expand=False, padx=12)
        if data.get("isi_soal"):
            soal_text.insert("1.0", data.get("isi_soal"))

        ttk.Label(dialog, text="Jawaban").pack(anchor="w", padx=12, pady=6)
        jawab_text = scrolledtext.ScrolledText(dialog, height=6, wrap="word")
        jawab_text.pack(fill="both", expand=False, padx=12)
        if data.get("isi_jawaban"):
            jawab_text.insert("1.0", data.get("isi_jawaban"))

        gambar_frame = ttk.LabelFrame(dialog, text="Gambar")
        gambar_frame.pack(fill="both", expand=False, padx=12, pady=8)
        gambar_list = tk.Listbox(gambar_frame, height=5)
        gambar_list.pack(fill="both", expand=True, padx=6, pady=6)
        gambar_items = data.get("gambar_paths", [])

        def refresh_gambar_list():
            gambar_list.delete(0, tk.END)
            for i, item in enumerate(gambar_items, 1):
                name = os.path.basename(item.get("path", ""))
                caption = item.get("caption", "")
                gambar_list.insert(tk.END, f"{i}. {name} - {caption}")

        def add_gambar():
            path = filedialog.askopenfilename(
                title="Pilih Gambar",
                filetypes=[("Image", "*.png;*.jpg;*.jpeg;*.bmp")],
            )
            if not path:
                return
            caption = self._prompt_caption()
            if caption is None:
                return
            gambar_items.append({"path": path, "caption": caption})
            refresh_gambar_list()

        def remove_gambar():
            sel = gambar_list.curselection()
            if not sel:
                return
            idx = sel[0]
            del gambar_items[idx]
            refresh_gambar_list()

        toolbar = ttk.Frame(gambar_frame)
        toolbar.pack(fill="x", padx=6, pady=4)
        ttk.Button(toolbar, text="Tambah Gambar", command=add_gambar).pack(
            side="left"
        )
        ttk.Button(toolbar, text="Hapus", command=remove_gambar).pack(
            side="left", padx=6
        )

        refresh_gambar_list()

        result = {"value": None}

        def on_save():
            judul = judul_var.get().strip()
            if not judul:
                messagebox.showwarning("Validasi", "Topik tugas belum diisi.")
                return

            soal = soal_text.get("1.0", "end-1c").strip()
            jawab = jawab_text.get("1.0", "end-1c").strip()
            if not soal or not jawab:
                messagebox.showwarning("Validasi", "Soal dan jawaban wajib diisi.")
                return

            result["value"] = {
                "judul_sub_bab": judul,
                "isi_soal": soal_text.get("1.0", "end-1c"),
                "isi_jawaban": jawab_text.get("1.0", "end-1c"),
                "gambar_paths": gambar_items,
            }
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        action_frame = ttk.Frame(dialog)
        action_frame.pack(fill="x", padx=12, pady=10)
        ttk.Button(action_frame, text="Simpan", command=on_save).pack(
            side="right", padx=6
        )
        ttk.Button(action_frame, text="Batal", command=on_cancel).pack(side="right")

        self.wait_window(dialog)
        return result["value"]

    def _open_kode_dialog(self, initial=None):
        dialog = tk.Toplevel(self)
        dialog.title("File Kode")
        dialog.geometry("640x520")
        dialog.transient(self)
        dialog.grab_set()

        nama_var = tk.StringVar(value=(initial or {}).get("nama", ""))
        ttk.Label(dialog, text="Nama File").pack(anchor="w", padx=12, pady=6)
        ttk.Entry(dialog, textvariable=nama_var, width=50).pack(anchor="w", padx=12)

        ttk.Label(dialog, text="Isi Kode").pack(anchor="w", padx=12, pady=6)
        isi_text = scrolledtext.ScrolledText(dialog, height=16, wrap="none")
        isi_text.pack(fill="both", expand=True, padx=12)
        if initial and initial.get("isi"):
            isi_text.insert("1.0", initial.get("isi"))

        result = {"value": None}

        def on_save():
            nama = nama_var.get().strip()
            isi = isi_text.get("1.0", "end-1c")
            if not isi.strip():
                messagebox.showwarning("Validasi", "Isi kode tidak boleh kosong.")
                return
            result["value"] = {"nama": nama, "isi": isi}
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        action_frame = ttk.Frame(dialog)
        action_frame.pack(fill="x", padx=12, pady=10)
        ttk.Button(action_frame, text="Simpan", command=on_save).pack(
            side="right", padx=6
        )
        ttk.Button(action_frame, text="Batal", command=on_cancel).pack(side="right")

        self.wait_window(dialog)
        return result["value"]

    def _prompt_caption(self):
        dialog = tk.Toplevel(self)
        dialog.title("Caption")
        dialog.geometry("420x160")
        dialog.transient(self)
        dialog.grab_set()

        caption_var = tk.StringVar()
        ttk.Label(dialog, text="Caption").pack(anchor="w", padx=12, pady=8)
        ttk.Entry(dialog, textvariable=caption_var, width=48).pack(anchor="w", padx=12)

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

    def _concat_kode_for_prompt(self, kode_items):
        parts = []
        for item in kode_items:
            name = item.get("nama") or ""
            content = item.get("isi") or ""
            header = f"File: {name}" if name else "File"
            parts.append(f"{header}\n{content}")
        return "\n\n".join(parts)

    def _generate(self):
        template_path = (
            os.path.join(TEMPLATES_DIR, "format-1.docx")
            if self.template_choice.get() == "1"
            else os.path.join(TEMPLATES_DIR, "format-2.docx")
        )
        if not os.path.exists(template_path):
            messagebox.showerror(
                "Template Tidak Ada",
                f"File template '{template_path}' tidak ditemukan.",
            )
            return

        cover = {}
        for key, var in self.cover_vars.items():
            cover[key] = var.get().strip()

        required = ["mata_kuliah", "nomor_modul", "judul", "nama", "nim", "tahun"]
        if any(not cover[k] for k in required):
            messagebox.showwarning("Validasi", "Data cover belum lengkap.")
            return

        cover["mata_kuliah"] = cover["mata_kuliah"].upper()
        cover["judul"] = cover["judul"].upper()
        cover["nama"] = cover["nama"].upper()

        kesimpulan = self.kesimpulan_text.get("1.0", "end-1c") if self.kesimpulan_text else ""
        if not kesimpulan.strip():
            messagebox.showwarning("Validasi", "Kesimpulan belum diisi.")
            return

        output_name = f"Laporan_Modul_{cover['nomor_modul']}_{cover['nama'].replace(' ', '_')}.docx"
        output_path = filedialog.asksaveasfilename(
            title="Simpan Laporan",
            defaultextension=".docx",
            initialfile=output_name,
            filetypes=[("Word Document", "*.docx")],
        )
        if not output_path:
            return

        doc = DocxTemplate(template_path)
        daftar_sub_bab = self._build_bab1_context(doc)
        daftar_tugas = self._build_bab2_context(doc)

        context = {
            **cover,
            "daftar_sub_bab": daftar_sub_bab,
            "daftar_tugas": daftar_tugas,
            "isi_kesimpulan": kesimpulan,
        }

        try:
            doc.render(context)
            doc.save(output_path)
            messagebox.showinfo("Sukses", f"Laporan tersimpan di:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Gagal", f"Gagal render: {e}")

    def _build_bab1_context(self, doc):
        daftar_sub_bab = []
        counter_gbr_bab1 = 1
        for item in self.bab1_items:
            label_a = "Source Code" if item.get("tipe") == "1" else "Langkah Kerja"
            isi_a = item.get("isi_a", "") if item.get("tipe") == "2" else ""

            kode_items = item.get("kode_files", [])
            list_kode_final = []
            if len(kode_items) > 0:
                for i, d in enumerate(kode_items, 1):
                    judul_tampil = f"{i}. {d['nama']}" if len(kode_items) > 1 else ""
                    list_kode_final.append({"judul": judul_tampil, "isi": d.get("isi", "")})

            list_gbr = []
            for g in item.get("gambar_paths", []):
                obj = muat_gambar(doc, g.get("path", ""))
                if not obj:
                    continue
                list_gbr.append(
                    {
                        "objek_gambar": obj,
                        "caption": g.get("caption", ""),
                        "nomor_tampil": counter_gbr_bab1,
                    }
                )
                counter_gbr_bab1 += 1

            daftar_sub_bab.append(
                {
                    "judul_sub_bab": item.get("judul_sub_bab", ""),
                    "label_point_a": label_a,
                    "isi_point_a": isi_a,
                    "list_gambar": list_gbr,
                    "isi_analisa": item.get("analisa", ""),
                    "list_kode": list_kode_final,
                }
            )

        return daftar_sub_bab

    def _build_bab2_context(self, doc):
        daftar_tugas = []
        counter_gbr_bab2 = 1
        for item in self.bab2_items:
            list_gbr_tgs = []
            for g in item.get("gambar_paths", []):
                obj = muat_gambar(doc, g.get("path", ""))
                if not obj:
                    continue
                list_gbr_tgs.append(
                    {
                        "objek_gambar": obj,
                        "caption": g.get("caption", ""),
                        "nomor_tampil": counter_gbr_bab2,
                    }
                )
                counter_gbr_bab2 += 1

            daftar_tugas.append(
                {
                    "judul_sub_bab": item.get("judul_sub_bab", ""),
                    "isi_soal": item.get("isi_soal", ""),
                    "isi_jawaban": item.get("isi_jawaban", ""),
                    "ada_gambar": len(list_gbr_tgs) > 0,
                    "list_gambar": list_gbr_tgs,
                }
            )

        return daftar_tugas


if __name__ == "__main__":
    app = App()
    app.mainloop()
