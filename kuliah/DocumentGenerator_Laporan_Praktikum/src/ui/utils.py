"""utils.py - Shared utility functions for UI operations."""

import os
import re
import tempfile
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageGrab
from tkinterdnd2 import DND_FILES

from ui.constants import (
    CODE_EXTENSIONS,
    MAX_CODE_FILE_SIZE,
    MAX_IMAGE_FILE_SIZE,
    SUPPORTED_IMAGE_FORMATS,
)


class UIUtils:
    """Class-based UI utility toolkit."""

    @staticmethod
    def show_info(title: str, message: str, parent=None) -> None:
        messagebox.showinfo(title, message, parent=parent)

    @staticmethod
    def show_warning(title: str, message: str, parent=None) -> None:
        messagebox.showwarning(title, message, parent=parent)

    @staticmethod
    def show_error(title: str, message: str, parent=None) -> None:
        messagebox.showerror(title, message, parent=parent)

    @staticmethod
    def validate_code_file(file_path: str) -> tuple[bool, str]:
        if not os.path.exists(file_path):
            return False, f"File tidak ditemukan: {file_path}"

        _, ext = os.path.splitext(file_path)
        if ext.lower() not in CODE_EXTENSIONS:
            return False, f"Tipe file tidak didukung: {ext}"

        if not UIUtils.is_valid_file_size(file_path, MAX_CODE_FILE_SIZE):
            return (
                False,
                f"Ukuran file melebihi batas {MAX_CODE_FILE_SIZE / 1024 / 1024:.0f} MB",
            )

        return True, ""

    @staticmethod
    def validate_image_file(file_path: str) -> tuple[bool, str]:
        if not os.path.exists(file_path):
            return False, f"File tidak ditemukan: {file_path}"

        _, ext = os.path.splitext(file_path)
        if ext.lower() not in SUPPORTED_IMAGE_FORMATS:
            return False, f"Format gambar tidak didukung: {ext}"

        if not UIUtils.is_valid_file_size(file_path, MAX_IMAGE_FILE_SIZE):
            return (
                False,
                f"Ukuran gambar melebihi batas {MAX_IMAGE_FILE_SIZE / 1024 / 1024:.0f} MB",
            )

        return True, ""

    @staticmethod
    def is_valid_file_size(file_path: str, max_size: int) -> bool:
        try:
            return os.path.getsize(file_path) <= max_size
        except OSError:
            return False

    @staticmethod
    def safe_path_join(*parts) -> str:
        return os.path.normpath(os.path.join(*parts))

    @staticmethod
    def get_safe_filename(filename: str) -> str:
        invalid_chars = r'[<>:"/\\|?*]'
        safe_name = re.sub(invalid_chars, "_", filename)
        return safe_name.strip()

    @staticmethod
    def extract_dnd_file_paths(event) -> list[str]:
        if not hasattr(event, "data") or not event.data:
            return []

        data = event.data.strip("{} ")

        if "{" in data or "}" in data:
            paths = re.findall(r"\{([^}]+)\}", event.data)
            if paths:
                return paths

        if "\n" in data:
            paths = [p.strip() for p in data.split("\n") if p.strip()]
        else:
            paths = [data] if " " not in data else data.split()

        return [p for p in paths if p and os.path.exists(p)]

    @staticmethod
    def capture_screenshot() -> str:
        try:
            img = ImageGrab.grabclipboard()
            if img is None:
                raise ValueError("Clipboard tidak berisi gambar")

            fd, temp_path = tempfile.mkstemp(suffix=".png")
            os.close(fd)
            img.save(temp_path, "PNG")
            return temp_path
        except Exception as e:
            raise RuntimeError(f"Gagal capture screenshot: {e}")

    @staticmethod
    def load_image(image_path: str, size: tuple = None) -> Image.Image:
        img = Image.open(image_path)
        if size:
            img = img.resize(size, Image.Resampling.LANCZOS)
        return img

    @staticmethod
    def resize_image(image_path: str, max_width: int, max_height: int) -> Image.Image:
        img = Image.open(image_path)
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        return img

    @staticmethod
    def bytes_to_mb(bytes_size: int) -> float:
        return bytes_size / 1024 / 1024

    @staticmethod
    def format_file_size(bytes_size: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} TB"

    @staticmethod
    def parse_step_list(text: str) -> list[dict]:
        langkah_list = []
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        for i, line in enumerate(lines, 1):
            clean_line = re.sub(r"^[^\w\s\d]+", "", line).strip()
            match = re.match(r"^\s*(\d+)[\s\.\)\-]*\s*(.*)", clean_line)

            if match:
                nomor = match.group(1)
                teks = match.group(2).strip()
            else:
                nomor = str(i)
                teks = clean_line

            if teks:
                langkah_list.append({"nomor": nomor, "langkah_kerja": teks})

        return langkah_list

    @staticmethod
    def setup_dnd_for_listbox(listbox: tk.Listbox, callback) -> None:
        listbox.drop_target_register(DND_FILES)
        listbox.dnd_bind("<<Drop>>", callback)
