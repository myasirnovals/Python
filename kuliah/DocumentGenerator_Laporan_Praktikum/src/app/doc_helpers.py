import os
import tempfile
from PIL import Image, ImageOps

from docxtpl import InlineImage
from docx.shared import Mm

def muat_gambar(doc, path, lebar_mm=116.7):
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
        # 1. Buka Gambar
        img = Image.open(path)
        img = img.convert("RGB") 

        # 2. Tentukan Ukuran Target (Pixel untuk 300 DPI)
        target_w = 1378
        target_h = 909

        # 3. FORCE RESIZE (Tarik Paksa)
        img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # 4. TAMBAHKAN BORDER (BINGKAI)
        # border=2 artinya ketebalan garis 2 pixel (tipis manis)
        # fill='black' artinya warnanya hitam
        img = ImageOps.expand(img, border=2, fill='black')

        # 5. Simpan ke File Sementara
        temp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        img.save(temp_file.name, quality=95) 
        temp_path = temp_file.name
        temp_file.close()

        # 6. Kembalikan ke Word
        return InlineImage(doc, temp_path, width=Mm(lebar_mm))

    except Exception as e:
        print(f"⚠️ Gagal memproses gambar {path}: {e}")
        return ""