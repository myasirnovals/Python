import os
import tempfile
from PIL import Image, ImageOps

from docxtpl import InlineImage
from docx.shared import Mm

class ImageDocumentHelper:
    """Process and normalize images before attaching into Word templates."""

    def __init__(self, target_width_px=1378, target_height_px=909, border_px=2):
        self.target_width_px = target_width_px
        self.target_height_px = target_height_px
        self.border_px = border_px
        self._temp_files = []

    def muat_gambar(self, doc, path, lebar_mm=116.7):
        """
        Fungsi FORCE RESIZE + BORDER:
        1. Memaksa gambar menjadi ukuran 11,67 cm x 7,7 cm (Gepeng jika perlu).
        2. Menambahkan BORDER HITAM tipis di sekeliling gambar agar tegas.
        """
        if not os.path.exists(path):
            if path.strip() != "":
                print(f"⚠️  File gambar '{path}' tidak ditemukan.")
            return ""

        try:
            with Image.open(path) as src:
                img = ImageOps.exif_transpose(src).convert("RGB")
            img = img.resize(
                (self.target_width_px, self.target_height_px),
                Image.Resampling.LANCZOS,
            )
            img = ImageOps.expand(img, border=self.border_px, fill="black")

            temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            temp_path = temp_file.name
            temp_file.close()
            img.save(temp_path, quality=95)
            self._temp_files.append(temp_path)

            return InlineImage(doc, temp_path, width=Mm(lebar_mm))
        except Exception as e:
            print(f"⚠️ Gagal memproses gambar {path}: {e}")
            return ""

    def cleanup_temp_files(self):
        """Hapus gambar sementara setelah dokumen selesai dirender & disimpan."""
        while self._temp_files:
            temp_path = self._temp_files.pop()
            try:
                os.remove(temp_path)
            except OSError:
                pass
