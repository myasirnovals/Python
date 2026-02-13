from app.prompts import build_prompt, instruksi_gaya


class AnalysisService:
    def __init__(self, ai_client):
        self.ai_client = ai_client
        self.ai_ready = False

    def ensure_ready(self):
        if self.ai_ready:
            return True
        if not self.ai_client.get_active_model():
            return False
        self.ai_ready = True
        return True

    @staticmethod
    def concat_kode_for_prompt(kode_items):
        parts = []
        for item in kode_items:
            name = item.get("nama") or ""
            content = item.get("isi") or ""
            header = f"File: {name}" if name else "File"
            parts.append(f"{header}\n{content}")
        return "\n\n".join(parts)

    def generate_analysis(self, tipe, isi_a_text, kode_items, gambar_items, template_choice):
        if not self.ensure_ready():
            return None, "AI tidak bisa connect. Periksa API key."

        isi_a = isi_a_text
        if tipe == "1":
            isi_a = self.concat_kode_for_prompt(kode_items)

        prompt = build_prompt(tipe, isi_a, instruksi_gaya())
        image_path = gambar_items[0]["path"] if gambar_items else None
        result = self.ai_client.ask(prompt, image_path)

        if template_choice == "1" and result:
            result = result.replace("\n\n", "\n")
            result = "\t" + result.replace("\n", "\n\t")

        return result, None
