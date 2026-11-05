BOBOT = {
    "A": 4.0,
    "B": 3.0,
    "C": 2.0,
    "D": 1.0,
    "E": 0.0,
    "F": 0.0,
}

def hitung_ipk(nilai_list):
    total_bobot=0.0
    total_sks=0
    for nilai in nilai_list:
        huruf=nilai["huruf"]
        sks=nilai["sks"]
        if huruf not in BOBOT:
            raise ValueError(f"Nilai huruf tidak dikenal: {huruf}")
        total_bobot += BOBOT[huruf]*sks
        total_sks += sks
    if total_sks==0:
        return 0.0
    return total_bobot/total_sks
