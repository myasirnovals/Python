import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext


class Bab2Tab(ttk.Frame):
    def __init__(self, app, parent):
        super().__init__(parent, padding=20)
        self.app = app
        self.bab2_items = []
        self._build()

    def _build(self):
        self.pack(fill="both", expand=True)

        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(
            header_frame, text="Daftar Tugas Praktikum", style="Header.TLabel"
        ).pack(side="left")

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(
            btn_frame, text="+ Tambah Sub-Bab Tugas", command=self._add_bab2
        ).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="✏️ Edit", command=self._edit_bab2).pack(
            side="left", padx=2
        )
        ttk.Button(btn_frame, text="🗑️ Hapus", command=self._remove_bab2).pack(
            side="left", padx=2
        )

        list_container = ttk.Frame(self)
        list_container.pack(fill="both", expand=True)

        self.bab2_listbox = tk.Listbox(
            list_container,
            font=("Segoe UI", 11),
            borderwidth=1,
            relief="flat",
            selectbackground="#007bff",
            highlightthickness=0,
            activestyle="none",
        )
        self.bab2_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            list_container, orient="vertical", command=self.bab2_listbox.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.bab2_listbox.config(yscrollcommand=scrollbar.set)

    def get_items(self):
        return self.bab2_items

    def _refresh_bab2_list(self):
        self.bab2_listbox.delete(0, tk.END)
        for i, item in enumerate(self.bab2_items, 1):
            judul = item.get("judul_sub_bab") or f"Tugas {i}"
            self.bab2_listbox.insert(tk.END, f"{i}. {judul}")

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

    def _open_bab2_dialog(self, initial=None):
        dialog = tk.Toplevel(self)
        dialog.title("Tugas Praktikum")
        dialog.geometry("760x640")
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self)
        dialog.grab_set()

        data = initial.copy() if initial else {}

        judul_var = tk.StringVar(value=data.get("judul_sub_bab", ""))
        ttk.Label(dialog, text="Topik Tugas").pack(anchor="w", padx=12, pady=6)
        ttk.Entry(dialog, textvariable=judul_var, width=60).pack(
            anchor="w", padx=12
        )

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

    def _prompt_caption(self):
        dialog = tk.Toplevel(self)
        dialog.title("Caption")
        dialog.geometry("420x160")
        dialog.configure(bg="#f8f9fa")
        dialog.transient(self)
        dialog.grab_set()

        caption_var = tk.StringVar()
        ttk.Label(dialog, text="Caption").pack(anchor="w", padx=12, pady=8)
        ttk.Entry(dialog, textvariable=caption_var, width=48).pack(
            anchor="w", padx=12
        )

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