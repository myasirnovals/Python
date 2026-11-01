"""Code and image attachment mixin for code-image tab."""

import ctypes
import os
import tempfile
import tkinter as tk
from tkinter import filedialog, ttk

from PIL import ImageGrab

from ui.constants import CODE_EXTENSIONS, CODE_FILETYPE_PATTERN, MAX_CODE_FILE_SIZE
from ui.utils import UIUtils


class CodeImageAttachmentsMixin:
    """Handle source-code files and screenshot/image attachments."""

    def _on_kode_drop(self, event):
        files = UIUtils.extract_dnd_file_paths(event)
        for file_path in files:
            if self._is_allowed_code_file(file_path):
                self._add_code_file(file_path, os.path.basename(file_path))
            else:
                self.show_warning(
                    "File Tidak Didukung",
                    f"File {os.path.basename(file_path)} bukan source code.",
                )

    def _on_gambar_drop(self, event):
        files = UIUtils.extract_dnd_file_paths(event)
        for file_path in files:
            if self._is_image_file(file_path):
                self.gambar_items.append(
                    {"path": file_path, "caption": os.path.basename(file_path)}
                )
                self._refresh_dialog_lists()
            else:
                self.show_warning(
                    "File Tidak Didukung",
                    f"File {os.path.basename(file_path)} bukan gambar yang didukung.",
                )

    def _add_kode(self):
        path = filedialog.askopenfilename(
            title="Pilih File Source Code",
            filetypes=[("Source Code", CODE_FILETYPE_PATTERN), ("All Files", "*.*")],
        )
        if not path:
            return

        self._add_code_file(path, os.path.basename(path))

    def _remove_kode(self):
        if self.kode_listbox.curselection():
            self.kode_items.pop(self.kode_listbox.curselection()[0])
            self._refresh_dialog_lists()
            self.kode_title_var.set("")

    def _add_gambar(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if path:
            self.gambar_items.append({"path": path, "caption": os.path.basename(path)})
            self._refresh_dialog_lists()

    def _remove_gambar(self):
        if self.gambar_listbox.curselection():
            self.gambar_items.pop(self.gambar_listbox.curselection()[0])
            self._refresh_dialog_lists()
            self.gambar_caption_var.set("")

    def _capture_gambar(self):
        main_window = self.winfo_toplevel()

        windows_to_hide = []
        if main_window.winfo_exists():
            windows_to_hide.append(main_window)

        for child in main_window.winfo_children():
            if isinstance(child, tk.Toplevel) and child.winfo_exists():
                windows_to_hide.append(child)

        for window in windows_to_hide:
            try:
                window.withdraw()
            except tk.TclError:
                continue

        # Jeda 250ms wajib agar Windows DWM menyelesaikan proses minimize/hide
        # sebelum overlay ditampilkan, mencegah jendela utama macet sebagai kotak putih tak ter-repaint.
        self.after(250, lambda: self._start_capture_overlay(main_window, windows_to_hide))

    def _start_capture_overlay(self, main_window, windows_to_hide):
        try:
            user32 = ctypes.windll.user32
            virt_x = user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
            virt_y = user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
            virt_w = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
            virt_h = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
            if virt_w <= 0 or virt_h <= 0:
                raise ValueError("Invalid virtual screen dimensions")
        except Exception:
            virt_x, virt_y = 0, 0
            virt_w = main_window.winfo_screenwidth()
            virt_h = main_window.winfo_screenheight()

        overlay = tk.Toplevel(main_window)
        overlay.overrideredirect(True)
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.30)
        overlay.configure(bg="black")

        pos_x = f"+{virt_x}" if virt_x >= 0 else f"{virt_x}"
        pos_y = f"+{virt_y}" if virt_y >= 0 else f"{virt_y}"
        overlay.geometry(f"{virt_w}x{virt_h}{pos_x}{pos_y}")

        try:
            top_hwnd = ctypes.windll.user32.GetParent(overlay.winfo_id()) or overlay.winfo_id()
            ctypes.windll.user32.SetWindowPos(
                top_hwnd, -1, virt_x, virt_y, virt_w, virt_h, 0x0050
            )
        except Exception:
            pass

        canvas = tk.Canvas(overlay, cursor="cross", bg="black", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        hint_frame = ttk.Frame(overlay, padding=(14, 8))
        hint_frame.place(relx=0.5, y=25, anchor="n")
        ttk.Label(
            hint_frame,
            text="📷 Klik & drag area untuk screenshot  |  ESC / Klik kanan untuk batal",
            font=("Segoe UI", 10, "bold"),
        ).pack()

        state = {"start": None, "rect": None, "label": None, "selection": None}
        restored = {"done": False}

        def restore_main_window():
            if restored["done"]:
                return
            restored["done"] = True

            for window in windows_to_hide:
                try:
                    window.deiconify()
                    window.lift()
                except tk.TclError:
                    continue

            try:
                main_window.focus_force()
            except tk.TclError:
                pass

        def cancel_capture(_event=None):
            try:
                overlay.grab_release()
            except tk.TclError:
                pass
            if overlay.winfo_exists():
                overlay.destroy()
            restore_main_window()

        def on_press(event):
            state["start"] = (event.x, event.y)
            if state["rect"] is not None:
                canvas.delete(state["rect"])
            if state["label"] is not None:
                canvas.delete(state["label"])
            state["rect"] = canvas.create_rectangle(
                event.x, event.y, event.x, event.y, outline="#00ffcc", width=2
            )

        def on_drag(event):
            if state["rect"] is not None and state["start"]:
                x0, y0 = state["start"]
                canvas.coords(state["rect"], x0, y0, event.x, event.y)
                w_box = abs(event.x - x0)
                h_box = abs(event.y - y0)
                if state["label"] is not None:
                    canvas.delete(state["label"])
                state["label"] = canvas.create_text(
                    min(x0, event.x) + 5,
                    max(y0, event.y) + 15,
                    text=f"{w_box} x {h_box} px",
                    fill="#00ffcc",
                    font=("Segoe UI", 9, "bold"),
                    anchor="w",
                )

        def on_release(event):
            if not state["start"]:
                return
            x1, y1 = state["start"]
            x2, y2 = event.x, event.y

            w_sel = abs(x2 - x1)
            h_sel = abs(y2 - y1)

            # Abaikan klik kecil tanpa sengaja (< 10 piksel)
            if w_sel < 10 or h_sel < 10:
                cancel_capture()
                return

            state["selection"] = (
                min(x1, x2) + virt_x,
                min(y1, y2) + virt_y,
                max(x1, x2) + virt_x,
                max(y1, y2) + virt_y,
            )
            perform_capture()

        def perform_capture():
            # 1. Lepas grab dan sembunyikan overlay agar tidak terfoto
            try:
                overlay.grab_release()
            except tk.TclError:
                pass

            if overlay.winfo_exists():
                overlay.withdraw()
                overlay.update()

            # 2. Ambil screenshot SEBELUM main_window dipulihkan agar target tidak tertutup!
            captured_file = None
            capture_err = None
            if state["selection"]:
                try:
                    bbox = state["selection"]
                    img = ImageGrab.grab(bbox=bbox)
                    fd, temp_path = tempfile.mkstemp(suffix=".png")
                    os.close(fd)
                    img.save(temp_path, "PNG")
                    captured_file = temp_path
                except Exception as e:
                    capture_err = str(e)

            # 3. Hancurkan overlay dan pulihkan jendela utama
            if overlay.winfo_exists():
                overlay.destroy()
            restore_main_window()

            # 4. Tambahkan hasil tangkapan layar jika berhasil
            if captured_file:
                default_caption = f"Screenshot {len(self.gambar_items) + 1}"
                self.gambar_items.append({"path": captured_file, "caption": default_caption})
                self._refresh_dialog_lists()
            elif capture_err:
                self.show_error("Capture Error", f"Gagal capture: {capture_err}")

        canvas.bind("<Button-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        canvas.bind("<Escape>", cancel_capture)
        canvas.bind("<Button-3>", cancel_capture)
        overlay.bind("<Escape>", cancel_capture)
        overlay.bind("<Button-3>", cancel_capture)
        overlay.protocol("WM_DELETE_WINDOW", cancel_capture)

        try:
            overlay.grab_set()
        except tk.TclError:
            pass
        overlay.focus_force()

    def _add_code_file(self, path, title):
        if not self._is_allowed_code_file(path):
            self.show_warning(
                "File Tidak Didukung",
                "Ekstensi file tidak termasuk daftar source code yang diizinkan.",
            )
            return
        try:
            content = self._read_code_file_safe(path)
            self.kode_items.append(
                {
                    "judul": title.strip() or os.path.basename(path),
                    "nama": os.path.basename(path),
                    "isi": content,
                }
            )
            self._refresh_dialog_lists()
        except Exception as e:
            self.show_error("Error", f"Gagal membaca file: {e}")

    def _refresh_dialog_lists(self):
        if self.kode_listbox is not None:
            self.kode_listbox.delete(0, tk.END)
            for f in self.kode_items:
                display_name = f.get("judul") or f.get("nama")
                self.kode_listbox.insert(tk.END, f"📄 {display_name}")

        if self.gambar_listbox is not None:
            self.gambar_listbox.delete(0, tk.END)
            for g in self.gambar_items:
                name = os.path.basename(g["path"])
                self.gambar_listbox.insert(tk.END, f"🖼️ {name} ({g['caption']})")

    def _on_kode_select(self, _event=None):
        if not self.kode_listbox.curselection():
            self.kode_title_var.set("")
            return
        idx = self.kode_listbox.curselection()[0]
        current = self.kode_items[idx]
        self.kode_title_var.set(current.get("judul") or current.get("nama", ""))

    def _apply_kode_title(self):
        if not self.kode_listbox.curselection():
            self.show_warning("Validasi", "Pilih file kode terlebih dahulu.")
            return
        idx = self.kode_listbox.curselection()[0]
        new_title = self.kode_title_var.get().strip()
        if not new_title:
            self.show_warning("Validasi", "Judul tidak boleh kosong.")
            return
        self.kode_items[idx]["judul"] = new_title
        self._refresh_dialog_lists()
        self.kode_listbox.selection_set(idx)

    def _on_gambar_select(self, _event=None):
        if not self.gambar_listbox.curselection():
            self.gambar_caption_var.set("")
            return
        idx = self.gambar_listbox.curselection()[0]
        self.gambar_caption_var.set(self.gambar_items[idx].get("caption", ""))

    def _apply_gambar_caption(self):
        if not self.gambar_listbox.curselection():
            self.show_warning("Validasi", "Pilih gambar terlebih dahulu.")
            return
        idx = self.gambar_listbox.curselection()[0]
        new_caption = self.gambar_caption_var.get().strip()
        if not new_caption:
            self.show_warning("Validasi", "Caption tidak boleh kosong.")
            return
        self.gambar_items[idx]["caption"] = new_caption
        self._refresh_dialog_lists()
        self.gambar_listbox.selection_set(idx)

    def _is_allowed_code_file(self, path):
        ext = os.path.splitext(path)[1].lower()
        return ext in CODE_EXTENSIONS

    def _is_image_file(self, path):
        ext = os.path.splitext(path)[1].lower()
        return ext in {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff"}

    def _read_code_file_safe(self, path):
        if not os.path.isfile(path):
            raise ValueError("Path file tidak valid.")

        if os.path.getsize(path) > MAX_CODE_FILE_SIZE:
            raise ValueError(
                f"Ukuran file terlalu besar (maksimal {MAX_CODE_FILE_SIZE / 1024 / 1024:.0f} MB)."
            )

        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        return content.replace("\x00", "")
