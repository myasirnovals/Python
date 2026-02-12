import os

from docxtpl import InlineImage
from docx.shared import Mm


def muat_gambar(doc, path, lebar_mm=120):
    if os.path.exists(path):
        return InlineImage(doc, path, width=Mm(lebar_mm))
    if path.strip() != "":
        print(f"⚠️  File gambar '{path}' tidak ditemukan.")
    return ""
