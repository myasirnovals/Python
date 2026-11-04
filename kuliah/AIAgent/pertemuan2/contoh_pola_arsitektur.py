"""Contoh pola arsitektur agentic; demo offline tanpa LLM/API."""
from concurrent.futures import ThreadPoolExecutor

def ambil_data(topik): return f"[ambil-data] Data terkait: {topik}"
def ringkas(teks): return f"[ringkasan] {teks}"
def cek(teks): return f"[cek] Kelengkapan: {teks}"

def prompt_chaining(topik):
    a=ambil_data(topik); b=ringkas(a); c=cek(b)
    return {"langkah_1":a,"langkah_2":b,"langkah_3":c}

def routing(q):
    t=q.lower()
    jalur="akademik" if any(x in t for x in ["jadwal","kelas"]) else "beasiswa" if "beasiswa" in t else "nilai" if any(x in t for x in ["nilai","ipk"]) else "klarifikasi"
    return {"permintaan":q,"jalur":jalur}

def parallelization(topik):
    tugas=[lambda:f"Fakta utama tentang {topik}",lambda:f"Risiko terkait {topik}",lambda:f"Pertanyaan evaluasi tentang {topik}"]
    with ThreadPoolExecutor(max_workers=3) as pool: return list(pool.map(lambda f:f(),tugas))

def orchestrator_workers(tugas):
    hasil={"data":f"Worker data: {tugas}","risiko":f"Worker risiko: {tugas}","uji":f"Worker uji: {tugas}"}
    return {"tugas":tugas,"hasil_workers":hasil,"sintesis":" | ".join(hasil.values())}

def evaluator_optimizer(draf,batas=3):
    versi=draf; trace=[]
    for i in range(1,batas+1):
        lolos=len(versi)>=30 and "catatan:" in versi.lower()
        trace.append({"iterasi":i,"panjang":len(versi),"lolos":lolos})
        if lolos: break
        versi="Catatan: "+versi+" — diperjelas dengan bukti dan batasan."
    return {"hasil":versi,"riwayat":trace}

if __name__=="__main__":
    print("1. Prompt chaining",prompt_chaining("asisten akademik"))
    print("\n2. Routing",[routing(q) for q in ["Jadwal besok","Syarat beasiswa","Cek IPK","Tolong bantu"]])
    print("\n3. Parallelization",parallelization("AI Agent"))
    print("\n4. Orchestrator-workers",orchestrator_workers("Rancang asisten akademik aman"))
    print("\n5. Evaluator-optimizer",evaluator_optimizer("Draf awal tanpa keterangan tambahan"))
