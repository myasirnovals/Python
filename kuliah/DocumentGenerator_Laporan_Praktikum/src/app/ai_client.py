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
        self.priority_models = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-3-flash-preview",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash-lite",
            "gemini-flash-lite-latest",
            "gemini-2.5-pro",
            "gemini-3-pro-preview"
        ]

    def get_active_model(self):
        """Mencari model terbaik dari daftar pilihan yang tersedia di akun Anda."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
        print("\n🔍 Mengecek ketersediaan model pilihan...")
        try:
            resp = requests.get(url)
            data = resp.json()
            if "error" in data:
                print(f"❌ Error API Key: {data['error']['message']}")
                return None

            available_models = [m["name"].replace("models/", "") for m in data.get("models", [])]

            # Pilih model pertama yang cocok dengan daftar prioritas kita
            for target in self.priority_models:
                if target in available_models:
                    self.model_name = target
                    print(f"✅ Otak Aktif: {self.model_name}")
                    return self.model_name

            # Fallback jika tidak ada satupun yang cocok
            if available_models:
                self.model_name = available_models[0]
                return self.model_name
            
            return None
        except Exception as e:
            print(f"❌ Gagal koneksi: {e}")
            return None
    
    def switch_model(self, prefer_pro=False):
        """Otomatis pindah ke model berikutnya dalam daftar prioritas jika model saat ini sibuk."""
        try:
            # Cari index model saat ini dalam daftar prioritas
            try:
                current_idx = self.priority_models.index(self.model_name)
            except ValueError:
                current_idx = -1
            
            # Ambil model berikutnya (loop kembali ke awal jika sudah di ujung daftar)
            next_idx = (current_idx + 1) % len(self.priority_models)
            self.model_name = self.priority_models[next_idx]
            
            print(f"🔄 Rotasi Otomatis: Pindah ke {self.model_name}...")
            return True
        except:
            return False

    def ask(self, prompt_text, image_path=None):
        if not self.model_name:
            if not self.get_active_model():
                return "Error: Tidak ada model."

        # Kita beri kesempatan mencoba lebih banyak (5 kali) 
        # karena sekarang kita punya banyak model cadangan untuk dicoba satu per satu
        for attempt in range(5): 
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"{self.model_name}:generateContent?key={self.api_key}"
            )
            headers = {"Content-Type": "application/json"}
            
            # --- [LOGIKA BISNIS ASLI: KONSTRUKSI PARTS] ---
            parts = [{"text": prompt_text}]
            if image_path and os.path.exists(image_path):
                try:
                    with open(image_path, "rb") as f:
                        b64_data = base64.b64encode(f.read()).decode("utf-8")
                        parts.append({
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": b64_data,
                            }
                        })
                except Exception as e:
                    print(f"⚠️ Gagal baca gambar: {e}")
            
            payload = {"contents": [{"parts": parts}]}

            try:
                # Menggunakan timeout agar jika koneksi gantung, sistem bisa langsung rotasi
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
                
                if response.status_code == 200:
                    # --- [LOGIKA BISNIS ASLI: PEMBERSIHAN TEKS] ---
                    # Bagian ini dipertahankan 100% sesuai kode rekan Anda
                    teks_hasil = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                    
                    # 1. Membersihkan tanda kutip & backtick
                    teks_bersih = teks_hasil.replace("'", "").replace("`", "").strip()
                    
                    # 2. Filter anti basa-basi
                    baris = teks_bersih.split("\n")
                    if len(baris) > 0:
                        kata_kunci = ["berikut adalah", "analisa:", "penjelasan:", "berdasarkan gambar"]
                        baris_pertama_lower = baris[0].lower()
                        
                        if any(k in baris_pertama_lower for k in kata_kunci) or baris[0].strip().endswith(":"):
                            baris = baris[1:]
                    
                    teks_final = "\n".join(baris).strip()
                    return teks_final

                elif response.status_code == 429:
                    # LOGIKA BARU: Jika sibuk, langsung rotasi ke model berikutnya di list prioritas
                    print(f"⚠️ Model {self.model_name} sibuk (429). Mencoba rotasi model...")
                    
                    # Memanggil fungsi switch_model yang baru (yang memakai list prioritas)
                    if self.switch_model():
                        # Tunggu sebentar (sistem tunggu) sebelum mencoba model baru
                        time.sleep(2)
                        continue 
                    else:
                        # Jika gagal switch, gunakan sistem tunggu lama (fallback)
                        wait = (attempt + 1) * 5
                        time.sleep(wait)
                
                else:
                    # Jika error lain (500, 503, dll), tetap coba rotasi model
                    print(f"❌ Error API {response.status_code}. Mencoba model lain...")
                    self.switch_model()
                    time.sleep(2)

            except Exception as e:
                # Jika terjadi error koneksi, pindah model dan tunggu sebentar
                print(f"⚠️ Koneksi bermasalah: {e}. Rotasi model...")
                self.switch_model()
                time.sleep(2)
        
        return "Gagal: Semua model sibuk atau terjadi error berulang."
