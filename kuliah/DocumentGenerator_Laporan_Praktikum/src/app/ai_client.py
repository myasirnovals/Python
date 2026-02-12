import base64
import json
import os
import time

import requests

from .config import API_KEY


class GeminiClient:
    def __init__(self, api_key=API_KEY):
        self.api_key = api_key
        self.model_name = None

    def get_active_model(self):
        """Mencari model Gemini yang HIDUP di akun Anda."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
        print("\n🔍 Sedang mencari model AI yang aktif...")
        try:
            resp = requests.get(url)
            data = resp.json()
            if "error" in data:
                print(f"❌ Error API Key: {data['error']['message']}")
                return None

            calon_model = []
            for m in data.get("models", []):
                nama = m["name"].replace("models/", "")
                if "gemini" in nama and "embedding" not in nama:
                    calon_model.append(nama)

            model_pilihan = None
            # Cari yang 'flash' dulu
            for m in calon_model:
                if "flash" in m:
                    model_pilihan = m
                    break

            # Kalau gak ada, ambil sembarang
            if not model_pilihan and calon_model:
                model_pilihan = calon_model[0]

            if model_pilihan:
                self.model_name = model_pilihan
                print(f"✅ Sistem Siap! Menggunakan Otak: {model_pilihan}")
                return model_pilihan

            print("❌ Tidak ada model Gemini yang ditemukan.")
            return None
        except Exception as e:
            print(f"❌ Gagal koneksi internet: {e}")
            return None

    def ask(self, prompt_text, image_path=None):
        if not self.model_name:
            if not self.get_active_model():
                return "Error: Tidak ada model."

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model_name}:generateContent?key={self.api_key}"
        )
        headers = {"Content-Type": "application/json"}

        parts = [{"text": prompt_text}]

        # Handle Gambar
        if image_path and os.path.exists(image_path):
            try:
                with open(image_path, "rb") as f:
                    b64_data = base64.b64encode(f.read()).decode("utf-8")
                    parts.append(
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": b64_data,
                            }
                        }
                    )
            except Exception as e:
                print(f"⚠️ Gagal baca gambar: {e}")

        payload = {"contents": [{"parts": parts}]}

        # Retry Logic (Anti-429)
        for i in range(5):
            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                if response.status_code == 200:
                    try:
                        teks_hasil = response.json()["candidates"][0]["content"]["parts"][0][
                            "text"
                        ]

                        # --- MEMBERSIHKAN TANDA KUTIP & BACKTICK ---
                        # Ini akan membuang tanda ' dan ` dari istilah teknis
                        teks_bersih = teks_hasil.replace("'", "").replace("`", "").strip()

                        # 2. FILTER ANTI BASA-BASI (Hapus kalimat pembuka AI)
                        baris = teks_bersih.split("\n")
                        # Jika baris pertama mengandung kata kunci basa-basi, hapus!
                        if len(baris) > 0:
                            kata_kunci = [
                                "berikut adalah",
                                "analisa:",
                                "penjelasan:",
                                "berdasarkan gambar",
                            ]
                            baris_pertama_lower = baris[0].lower()

                            # Cek apakah baris pertama itu cuma pengantar?
                            if any(k in baris_pertama_lower for k in kata_kunci) or baris[0].strip().endswith(
                                ":"
                            ):
                                # Kita buang baris pertama, ambil sisanya
                                baris = baris[1:]

                        # Gabungkan lagi (Hanya pakai \n satu kali agar RAPAT)
                        # strip() membuang spasi kosong di awal/akhir sisa teks
                        teks_final = "\n".join(baris).strip()

                        return teks_final
                    except Exception:
                        return "Error: Format jawaban aneh."
                if response.status_code == 429:
                    wait = (i + 1) * 5
                    print(f"      ⏳ Server sibuk, menunggu {wait} detik...")
                    time.sleep(wait)
                elif response.status_code == 404:
                    print("      🔄 Model hilang, mencari ulang...")
                    if not self.get_active_model():
                        return "Gagal: Model hilang."
                else:
                    return f"Gagal API: {response.status_code}"
            except Exception:
                time.sleep(2)

        return "Gagal: Server busy (Give up)."
