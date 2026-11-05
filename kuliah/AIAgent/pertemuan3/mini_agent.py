from pathlib import Path
import subprocess,sys

ROOT=Path(__file__).resolve().parent/"sample_project"
SOURCE=ROOT/"akademik.py"

def tool_grep(pattern):
    print(f"\n[TOOL] grep({pattern!r})")
    found=[]
    for path in ROOT.rglob("*.py"):
        if "tests" in path.parts: continue
        for n,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
            if pattern in line: found.append(f"{path.relative_to(ROOT)}:{n}: {line.strip()}")
    return "\n".join(found) or "Tidak ditemukan."

def tool_read_file(relative_path):
    print(f"\n[TOOL] read_file({relative_path})")
    path=(ROOT/relative_path).resolve()
    if ROOT.resolve() not in path.parents: raise ValueError("Akses di luar proyek ditolak.")
    return path.read_text(encoding="utf-8")

def tool_run_tests():
    print("\n[TOOL] run_tests()")
    result=subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-v"],
                          cwd=ROOT,text=True,capture_output=True)
    return result.returncode,result.stdout+result.stderr

def tool_edit_file(old,new):
    print("\n[TOOL] edit_file(akademik.py)")
    text=SOURCE.read_text(encoding="utf-8")
    if old not in text: return "Gagal: teks target tidak ditemukan."
    SOURCE.write_text(text.replace(old,new,1),encoding="utf-8")
    return "Berhasil: perubahan diterapkan."

def run_agent():
    task="Perbaiki hitung_ipk agar nilai E dikenali dengan bobot 0.0, lalu jalankan semua tes."
    context=[f"[USER] {task}"]
    print("="*68+"\nMINI AI CODING AGENT — PERBAIKAN BUG IPK\n"+"="*68)
    print("[CONTEXT]",task)
    print("\n[AGENT / SIMULASI] Cari definisi fungsi.")
    result=tool_grep("def hitung_ipk"); context.append("[OBSERVATION grep]\n"+result); print(result)
    print("\n[AGENT / SIMULASI] Baca file sumber.")
    result=tool_read_file("akademik.py"); context.append("[OBSERVATION read]\n"+result); print(result)
    print("\n[AGENT / SIMULASI] Jalankan tes awal.")
    code,result=tool_run_tests(); context.append("[OBSERVATION test]\n"+result); print(result)
    if code==0:
        print("Tes sudah lulus; tidak perlu edit."); return
    print("\n[AGENT DECISION / SIMULASI] Tambahkan bobot E = 0.0.")
    result=tool_edit_file('    "D": 1.0,\n','    "D": 1.0,\n    "E": 0.0,\n')
    context.append("[OBSERVATION edit]\n"+result); print(result)
    print("\n[AGENT / SIMULASI] Jalankan tes ulang.")
    code,result=tool_run_tests(); context.append("[OBSERVATION retest]\n"+result); print(result)
    print("\n[FINAL ANSWER]")
    print("Bug diperbaiki dan seluruh tes lulus." if code==0 else "Perbaikan belum berhasil.")
    print("Jumlah rekaman konteks/observasi:",len(context))
    print("Catatan: keputusan di demo ini berbasis aturan Python, bukan LLM terlatih.")

if __name__=="__main__": run_agent()
