"""utils.py - Shared utility functions for UI operations."""

import os
import re
import tempfile
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from PIL import Image, ImageGrab
from tkinterdnd2 import DND_FILES

from ui.constants import (
    CODE_EXTENSIONS,
    MAX_CODE_FILE_SIZE,
    SUPPORTED_IMAGE_FORMATS,
    MAX_IMAGE_FILE_SIZE,
    MSG_SUCCESS_TITLE,
    MSG_WARNING_TITLE,
    MSG_ERROR_TITLE,
)


def show_info(title: str, message: str, parent=None) -> None:
    """Display info message box."""
    messagebox.showinfo(title, message, parent=parent)


def show_warning(title: str, message: str, parent=None) -> None:
    """Display warning message box."""
    messagebox.showwarning(title, message, parent=parent)


def show_error(title: str, message: str, parent=None) -> None:
    """Display error message box."""
    messagebox.showerror(title, message, parent=parent)


def validate_code_file(file_path: str) -> tuple[bool, str]:
    """
    Validate if file is a supported code file.
    
    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is empty.
    """
    if not os.path.exists(file_path):
        return False, f"File tidak ditemukan: {file_path}"
    
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in CODE_EXTENSIONS:
        return False, f"Tipe file tidak didukung: {ext}"
    
    if not is_valid_file_size(file_path, MAX_CODE_FILE_SIZE):
        return False, f"Ukuran file melebihi batas {MAX_CODE_FILE_SIZE / 1024 / 1024:.0f} MB"
    
    return True, ""


def validate_image_file(file_path: str) -> tuple[bool, str]:
    """
    Validate if file is a supported image file.
    
    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is empty.
    """
    if not os.path.exists(file_path):
        return False, f"File tidak ditemukan: {file_path}"
    
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in SUPPORTED_IMAGE_FORMATS:
        return False, f"Format gambar tidak didukung: {ext}"
    
    if not is_valid_file_size(file_path, MAX_IMAGE_FILE_SIZE):
        return False, f"Ukuran gambar melebihi batas {MAX_IMAGE_FILE_SIZE / 1024 / 1024:.0f} MB"
    
    return True, ""


def is_valid_file_size(file_path: str, max_size: int) -> bool:
    """Check if file size is within limit."""
    try:
        return os.path.getsize(file_path) <= max_size
    except OSError:
        return False


def safe_path_join(*parts) -> str:
    """Safely join path parts."""
    return os.path.normpath(os.path.join(*parts))


def get_safe_filename(filename: str) -> str:
    """Remove or replace invalid filename characters."""
    # Replace common invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    safe_name = re.sub(invalid_chars, '_', filename)
    return safe_name.strip()


def extract_dnd_file_paths(event) -> list[str]:
    """
    Parse drag-and-drop file paths from event data.
    
    Handles both Windows and Unix formats.
    """
    if not hasattr(event, 'data') or not event.data:
        return []
    
    # Remove curly braces (Windows format) and split by space or newline
    data = event.data.strip('{} ')
    
    # Try to parse as curly-brace-enclosed paths (Windows)
    if '{' in data or '}' in data:
        # Extract paths enclosed in curly braces
        import re
        paths = re.findall(r'\{([^}]+)\}', event.data)
        if paths:
            return paths
    
    # Split by newline or whitespace
    if '\n' in data:
        paths = [p.strip() for p in data.split('\n') if p.strip()]
    else:
        # For single path without spaces
        paths = [data] if ' ' not in data else data.split()
    
    # Filter out empty strings and convert to valid paths
    return [p for p in paths if p and os.path.exists(p)]


def capture_screenshot() -> str:
    """Capture screenshot and save to temporary file."""
    try:
        img = ImageGrab.grabclipboard()
        if img is None:
            raise ValueError("Clipboard tidak berisi gambar")
        
        # Save to temp file
        fd, temp_path = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        img.save(temp_path, 'PNG')
        return temp_path
    except Exception as e:
        raise RuntimeError(f"Gagal capture screenshot: {e}")


def load_image(image_path: str, size: tuple = None) -> Image.Image:
    """Load and optionally resize image."""
    img = Image.open(image_path)
    if size:
        img = img.resize(size, Image.Resampling.LANCZOS)
    return img


def resize_image(image_path: str, max_width: int, max_height: int) -> Image.Image:
    """Resize image to fit within max dimensions while maintaining aspect ratio."""
    img = Image.open(image_path)
    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    return img


def bytes_to_mb(bytes_size: int) -> float:
    """Convert bytes to megabytes."""
    return bytes_size / 1024 / 1024


def format_file_size(bytes_size: int) -> str:
    """Format byte size to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def parse_step_list(text: str) -> list[dict]:
    """
    Parse step list from text format.
    
    Example input:
        "1. First step
         2. Second step
         3. Third step"
    
    Returns list of dicts with 'nomor' and 'langkah_kerja' keys.
    """
    langkah_list = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    
    for i, line in enumerate(lines, 1):
        # Clean non-printable characters at start
        clean_line = re.sub(r'^[^\w\s\d]+', '', line).strip()
        
        # Pattern: number at start + separator + text
        match = re.match(r'^\s*(\d+)[\s\.\)\-]*\s*(.*)', clean_line)
        
        if match:
            nomor = match.group(1)
            teks = match.group(2).strip()
        else:
            # No number found, use index
            nomor = str(i)
            teks = clean_line
        
        if teks:
            langkah_list.append({
                "nomor": nomor,
                "langkah_kerja": teks
            })
    
    return langkah_list


def setup_dnd_for_listbox(listbox: tk.Listbox, callback) -> None:
    """Configure drag-and-drop for a listbox."""
    listbox.drop_target_register(DND_FILES)
    listbox.dnd_bind('<<Drop>>', callback)
