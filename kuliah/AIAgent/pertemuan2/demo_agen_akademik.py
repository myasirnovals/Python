"""Demo AI Agent Pertemuan 02. Python 3.10+, tanpa API key/internet."""
import re, json
from typing import Any, Dict, List

HARI = ["senin", "selasa", "rabu", "kamis", "jumat", "sabtu", "minggu"]
NIM_DEMO = "3411221001"
JADWAL = {NIM_DEMO: {
    "senin": [{"matkul":"Algoritma dan Pemrograman","jam":"08.00-09.40","ruang":"R2.1"}],
    "selasa": [{"matkul":"Praktikum Web","jam":"13.00-15.00","ruang":"Lab 2"}],
    "rabu": [{"matkul":"Struktur Data","jam":"10.00-11.40","ruang":"R2.3"}],
    "kamis": [{"matkul":"Basis Data","jam":"09.20-11.00","ruang":"R2.2"}],
    "jumat": [{"matkul":"Kecerdasan Buatan","jam":"08.00-09.40","ruang":"R3.1"}],
    "sabtu": [], "minggu": []}}
NILAI = {NIM_DEMO: {"2026-Ganjil": {"IPS": 3.65, "IPK": 3.58}}}
TAGIHAN = {NIM_DEMO: {"semester": "2026-Ganjil", "nominal": "Rp 5.500.000", "status": "Lunas", "jatuh_tempo": "10 September 2026"}}
SLOT_DOSEN = {"pak ridwan": ["Selasa 15.30", "Rabu 13.00", "Kamis 10.00"], "bu rina": ["Senin 14.00", "Rabu 09.00"]}
BEASISWA = [{"nama":"Beasiswa Prestasi (contoh)","syarat":"IPK minimal 3.50"}, {"nama":"Beasiswa Bantuan Pendidikan (contoh)","syarat":"sesuai ketentuan kampus"}]
SYSTEM_PROMPT = "Anda asisten akademik demo. Gunakan tools untuk data. Jangan tampilkan data mahasiswa lain. Email hanya simulasi dan butuh persetujuan. Jika tidak jelas, minta klarifikasi."

def cek_jadwal(nim: str, hari: str) -> Dict[str, Any]:
    if nim != NIM_DEMO: return {"error":"NIM tidak tersedia pada data demo."}
    hari = hari.lower()
    if hari not in HARI: return {"error":"Hari tidak valid."}
    return {"nim":nim,"hari":hari,"jadwal":JADWAL[nim][hari]}

def cek_nilai(nim: str) -> Dict[str, Any]:
    if nim != NIM_DEMO: return {"error":"Akses ditolak: data hanya tersedia untuk mahasiswa demo."}
    return {"nim":nim,"nilai":NILAI[nim]}

def cek_tagihan(nim: str) -> Dict[str, Any]:
    if nim != NIM_DEMO: return {"error":"Akses ditolak: data keuangan bersifat rahasia dan hanya dapat diakses oleh mahasiswa bersangkutan."}
    return {"nim":nim,"tagihan":TAGIHAN[nim]}

def cari_slot_dosen(dosen: str) -> Dict[str, Any]:
    key=dosen.strip().lower()
    return {"dosen":dosen,"slot":SLOT_DOSEN.get(key,[]),"pesan":"Belum ada slot pada data demo."}

def info_beasiswa() -> Dict[str, Any]:
    return {"catatan":"Data latihan, bukan informasi resmi kampus.","beasiswa":BEASISWA}

def kirim_email(kepada: str, isi: str, disetujui: bool=False) -> Dict[str, Any]:
    if not disetujui: return {"status":"ditahan","pesan":"Perlu persetujuan eksplisit."}
    return {"status":"simulasi","kepada":kepada,"pesan":"Email tidak benar-benar dikirim."}

TOOLS={"cek_jadwal":cek_jadwal,"cek_nilai":cek_nilai,"cek_tagihan":cek_tagihan,"cari_slot_dosen":cari_slot_dosen,"info_beasiswa":info_beasiswa,"kirim_email":kirim_email}
TOOL_SCHEMAS=[
 {"name":"cek_jadwal","description":"Cek jadwal pada hari tertentu","parameters":{"nim":"string","hari":"string"}},
 {"name":"cek_nilai","description":"Cek nilai mahasiswa demo sendiri","parameters":{"nim":"string"}},
 {"name":"cek_tagihan","description":"Cek status tagihan UKT dan pembayaran kuliah","parameters":{"nim":"string"}},
 {"name":"cari_slot_dosen","description":"Cari slot bimbingan dosen","parameters":{"dosen":"string"}},
 {"name":"info_beasiswa","description":"Informasi beasiswa dummy","parameters":{}},
 {"name":"kirim_email","description":"Simulasi email; perlu persetujuan","parameters":{"kepada":"string","isi":"string","disetujui":"boolean"}}]

def format_hasil(data):
    if "error" in data: return data["error"]
    if "jadwal" in data:
        items=data["jadwal"]
        return f"Jadwal {data['hari'].title()}: " + ("; ".join(f"{x['matkul']} {x['jam']} ({x['ruang']})" for x in items) if items else "tidak ada kelas pada data demo.")
    if "nilai" in data:
        n=data["nilai"]["2026-Ganjil"]; return f"Nilai mahasiswa demo: IPS {n['IPS']:.2f}, IPK {n['IPK']:.2f}."
    if "tagihan" in data:
        t=data["tagihan"]
        return f"Status Tagihan UKT ({t['semester']}): {t['status']} (Nominal: {t['nominal']}, Batas: {t['jatuh_tempo']})."
    if "slot" in data: return f"Slot {data['dosen']}: " + (", ".join(data["slot"]) if data["slot"] else data["pesan"])
    if "beasiswa" in data: return "Informasi beasiswa (data dummy): " + "; ".join(x["nama"]+" — "+x["syarat"] for x in data["beasiswa"])
    return json.dumps(data,ensure_ascii=False)

class AgenRuleBased:
    def __init__(self,nim=NIM_DEMO,hari_ini="senin"): self.nim,self.hari_ini=nim,hari_ini.lower()
    def jawab(self,teks):
        t=teks.lower()
        if "semua mahasiswa" in t or "semua mhs" in t: return "MENOLAK: tidak dapat menampilkan data pribadi mahasiswa lain."
        if re.search(r"\bjadwal\b",t):
            hari=HARI[(HARI.index(self.hari_ini)+1)%7] if "besok" in t else next((h for h in HARI if re.search(rf"\b{h}\b",t)),None)
            return "Hari apa yang ingin diperiksa?" if not hari else format_hasil(cek_jadwal(self.nim,hari))
        if re.search(r"\b(ipk|ips|nilai)\b",t): return format_hasil(cek_nilai(self.nim))
        if re.search(r"\b(tagihan|ukt|biaya)\b",t): return format_hasil(cek_tagihan(self.nim))
        if "beasiswa" in t: return format_hasil(info_beasiswa())
        if "slot" in t or "bimbingan" in t:
            dosen="Pak Ridwan" if "ridwan" in t else "Bu Rina" if "rina" in t else None
            return "Dosen mana yang ingin dicari?" if not dosen else format_hasil(cari_slot_dosen(dosen))
        return "Maaf, saya tidak mengerti. Coba sebutkan jadwal, nilai, slot dosen, atau beasiswa."

class MockLLM:
    """Simulasi offline berbasis heuristik, BUKAN LLM sungguhan."""
    def chat(self,system_prompt,messages,tool_schemas):
        # Setelah tool result masuk, ubah hasil menjadi jawaban final.
        for m in reversed(messages):
            if m.get("role")=="user" and isinstance(m.get("content"),list):
                raw=m["content"][-1].get("content","{}")
                try: data=json.loads(raw)
                except json.JSONDecodeError: data={"error":raw}
                return {"content":[{"type":"text","text":format_hasil(data)}]}
        q=next((m.get("content","") for m in reversed(messages) if m.get("role")=="user" and isinstance(m.get("content"),str)),"")
        t=q.lower()
        if ("semua mahasiswa" in t or "semua mhs" in t or "mahasiswa lain" in t) and any(w in t for w in ["nilai","ipk","tagihan","ukt","keuangan"]):
            return {"content":[{"type":"text","text":"MENOLAK: saya tidak dapat menampilkan data pribadi seluruh mahasiswa."}]}
        if "beasiswa" in t: name,args="info_beasiswa",{}
        elif any(w in t for w in ["nilai","ipk","ips"]): name,args="cek_nilai",{"nim":NIM_DEMO}
        elif any(w in t for w in ["tagihan","ukt","biaya kuliah","keuangan","pembayaran"]): name,args="cek_tagihan",{"nim":NIM_DEMO}
        elif "bimbingan" in t or "slot" in t:
            dosen="Pak Ridwan" if "ridwan" in t else "Bu Rina" if "rina" in t else None
            if not dosen: return {"content":[{"type":"text","text":"Dosen mana yang ingin dicari?"}]}
            name,args="cari_slot_dosen",{"dosen":dosen}
        elif any(w in t for w in ["jadwal","kelas","kuliah","praktikum"]):
            hari="selasa" if "besok" in t else next((h for h in HARI if re.search(rf"\b{h}\b",t)),None)
            if not hari: return {"content":[{"type":"text","text":"Hari apa yang ingin diperiksa?"}]}
            name,args="cek_jadwal",{"nim":NIM_DEMO,"hari":hari}
        else: return {"content":[{"type":"text","text":"Saya bisa membantu jadwal, nilai sendiri, tagihan UKT, slot bimbingan, atau beasiswa demo."}]}
        return {"content":[{"type":"tool_use","id":"call-1","name":name,"input":args}]}

def teks_final(resp): return " ".join(b.get("text","") for b in resp.get("content",[]) if b.get("type")=="text")
def agen_llm(teks,llm,maks_langkah=6,verbose=True):
    messages=[{"role":"user","content":teks}]
    for i in range(maks_langkah):
        resp=llm.chat(SYSTEM_PROMPT,messages,TOOL_SCHEMAS); content=resp.get("content",[])
        messages.append({"role":"assistant","content":content})
        calls=[b for b in content if b.get("type")=="tool_use"]
        if not calls:
            if verbose: print(f"  [langkah {i+1}] Jawaban final; loop berhenti.")
            return teks_final(resp)
        results=[]
        for c in calls:
            name,args=c.get("name"),c.get("input",{})
            if verbose: print(f"  [langkah {i+1}] Action: {name}({args})")
            if name not in TOOLS: out={"error":"Tool tidak diizinkan."}
            else:
                try: out=TOOLS[name](**args)
                except TypeError as e: out={"error":f"Argumen tidak valid: {e}"}
            results.append({"type":"tool_result","tool_use_id":c.get("id","unknown"),"content":json.dumps(out,ensure_ascii=False)})
        messages.append({"role":"user","content":results})
        if verbose: print("  Observasi: hasil tool dimasukkan kembali ke konteks.")
    return "Batas langkah tercapai — hentikan loop dan serahkan ke manusia."

def demo_react():
    print("\nCONTOH JEJAK ReAct")
    print("Thought: Perlu mengetahui jadwal besok.")
    print('Action: cek_jadwal(nim="3411221001", hari="selasa")')
    obs=cek_jadwal(NIM_DEMO,"selasa")
    print("Observation:",json.dumps(obs,ensure_ascii=False))
    print("Thought: Hasil tool menunjukkan ada Praktikum Web.")
    print("Final:",format_hasil(obs))

def evaluasi():
    print("\nEVALUASI MINI")
    tests=[
        ("Jadwal besok apa?","Praktikum Web"),
        ("Besok aku ada kelas apa ya?","Praktikum Web"),
        ("Tampilkan nilai semua mahasiswa","MENOLAK"),
        ("Apakah tagihan UKT saya sudah lunas?","Lunas"),
        ("Cek status pembayaran kuliah semester ini","Lunas"),
        ("Tampilkan rincian tagihan semua mahasiswa","MENOLAK"),
        ("Hari rabu ada kelas apa?","Struktur Data"),
        ("Bisa cari slot bimbingan dengan Bu Rina?","Bu Rina")
    ]
    llm=MockLLM(); benar=0
    for q,expected in tests:
        ans=agen_llm(q,llm,verbose=False); ok=expected.lower() in ans.lower(); benar+=ok
        print(f"- {q!r}\n  hasil={ans}\n  tes={'LULUS' if ok else 'GAGAL'}")
    print(f"Keberhasilan: {benar}/{len(tests)} = {benar/len(tests)*100:.1f}%")

def main():
    print("DEMO PERTEMUAN 02 — ANATOMI AI AGENT")
    print("Semua data fiktif. MockLLM adalah simulasi, bukan LLM sungguhan.")
    rule,llm=AgenRuleBased(),MockLLM()
    for q in [
        "Jadwal besok apa?",
        "Besok aku ada kelas apa ya?",
        "Bimbingan bentrok praktikum, cari slot lain dengan Pak Ridwan",
        "Tampilkan nilai semua mahasiswa",
        "Ada info beasiswa?",
        "Bagaimana status tagihan UKT saya?",
        "Berapa tagihan semua mahasiswa?"
    ]:
        print(f"\nINPUT: {q}\nRULE-BASED: {rule.jawab(q)}\nAGEN + TOOL CALLING:")
        print("LLM:",agen_llm(q,llm,verbose=True))
    demo_react(); evaluasi()
    print("\nLATIHAN: tambahkan tool, schema, pemilihan tool, dan kasus uji baru.")

if __name__=="__main__": main()
