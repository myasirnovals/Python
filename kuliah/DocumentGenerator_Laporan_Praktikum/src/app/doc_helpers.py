import os
import tempfile
from PIL import Image

from docxtpl import InlineImage
from docx.shared import Mm

def muat_gambar(doc, path, lebar_mm=116.7):
    """
    Fungsi FORCE RESIZE (Paksa Penuh):
    Memaksa gambar menjadi ukuran 11,67 cm x 7,7 cm.
    
    PERINGATAN: 
    Gambar akan ditarik (stretch) agar pas. 
    Jika gambar asli kotak, akan terlihat gepeng melebar.
    Jika gambar asli panjang, akan terlihat gepeng memendek.
    Tapi HASILNYA PASTI PENUH tanpa sisa putih.
    """
    
    if not os.path.exists(path):
        if path.strip() != "":
            print(f"⚠️  File gambar '{path}' tidak ditemukan.")
        return ""

    try:
        # 1. Buka Gambar
        img = Image.open(path)
        img = img.convert("RGB") 

        # 2. Tentukan Ukuran Target (Pixel untuk 300 DPI)
        # Lebar 11,67 cm -> ~1378 pixel
        # Tinggi 7,7 cm  -> ~909 pixel
        target_w = 1378
        target_h = 909

        # 3. FORCE RESIZE (Tarik Paksa)
        # Kita ganti 'thumbnail' (jaga rasio) menjadi 'resize' (abaikan rasio)
        # Gambar akan melar mengikuti target_w dan target_h
        img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

        # 4. Simpan ke File Sementara
        temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        img.save(temp_file.name, quality=95) 
        temp_path = temp_file.name
        temp_file.close()

        # 5. Kembalikan ke Word
        return InlineImage(doc, temp_path, width=Mm(lebar_mm))

    except Exception as e:
        print(f"⚠️ Gagal memproses gambar {path}: {e}")
        return ""