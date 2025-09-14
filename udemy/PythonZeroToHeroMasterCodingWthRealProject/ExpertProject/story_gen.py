import random

when = [
    'Jutaan tahun yang lalu',
    'Selama proses pendinginan magma',
    'Saat sebuah ekspedisi geologi',
    'Di dalam sebuah laboratorium modern',
    'Setelah peristiwa tumbukan meteorit',
    'Selama proses kristalisasi hidrotermal'
]

who = [
    'seorang mineralogis terkenal',
    'seorang mahasiswa geologi yang ambisius',
    'seorang penambang tua yang berpengalaman',
    'seorang kolektor kristal yang antusias',
    'sebuah tim peneliti dari universitas',
    'seorang ahli petrologi'
]

name = [
    'Friedrich Mohs',
    'James Dana',
    'Dr. Budi',
    'Profesor Intan',
    'Andi',
    'Citra'
]

residence = [
    'di sebuah singkapan batuan beku',
    'di dasar gua kapur yang dalam',
    'di dekat kawah gunung berapi aktif',
    'di sebuah endapan sedimen purba',
    'di zona metamorfik bertekanan tinggi',
    'di sebuah museum geologi ternama'
]

went = [
    'meneliti sebuah pegmatit granit',
    'pergi ke tambang tembaga tua',
    'melakukan analisis difraksi sinar-X',
    'menguji kekerasan mineral dengan Skala Mohs',
    'mengamati sayatan tipis batuan di bawah mikroskop',
    'mencari jejak mineral sulfida di aliran sungai'
]

happened = [
    'menemukan kristal kuarsa yang berukuran sangat besar.',
    'mengidentifikasi sebuah mineral baru yang belum pernah tercatat.',
    'membuktikan bahwa batuan tersebut mengandung emas dalam jumlah signifikan.',
    'memahami proses pembentukan belahan sempurna pada mineral mika.',
    'menentukan komposisi kimia dari sebuah feldspar plagioklas.',
    'menemukan fosil di dalam lapisan batuan sedimen.'
]

print(f'{random.choice(when)}, {random.choice(who)} bernama {random.choice(name)} sedang berada {random.choice(residence)}, ia {random.choice(went)} dan {random.choice(happened)}')