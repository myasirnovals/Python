class Quiz:
    def __init__(self):
        self.questions = []

    def add_question(self, question, choices, correct_answer):
        self.questions.append({
            'question': question,
            'choices': choices,
            'correct_answer': correct_answer
        })

    def take_quiz(self):
        score = 0
        total_questions = len(self.questions)

        for i, q in enumerate(self.questions, start=1):
            print(f'Question {i}: {q['question']}')

            for idx, choice in enumerate(q['choices'], start=1):
                print(f'{idx}. {choice}')

            answer = input('Enter your choice number (1, 2, 3, ...): ')

            if answer.isdigit():
                user_answer = int(answer) - 1

                if 0 <= user_answer < len(q['choices']):
                    if q['choices'][user_answer] == q['correct_answer']:
                        score += 1

        print(f'\nYou scored {score} out of {total_questions} questions correctly.')

my_quiz = Quiz()

# Pertanyaan 1: Definisi Mineral
my_quiz.add_question(
    question='Manakah di bawah ini yang paling tepat mendefinisikan mineral?',
    choices=['A. Benda padat buatan manusia dengan struktur kristal.', 'B. Senyawa anorganik alami dengan komposisi kimia dan struktur kristal tertentu.', 'C. Batuan cair yang ditemukan di bawah permukaan bumi.', 'D. Segala jenis batuan yang ditemukan di alam.'],
    correct_answer='B. Senyawa anorganik alami dengan komposisi kimia dan struktur kristal tertentu.'
)

# Pertanyaan 2: Skala Kekerasan
my_quiz.add_question(
    question='Skala Mohs digunakan untuk mengukur sifat fisik mineral berupa...',
    choices=['A. Kilap (Luster)', 'B. Kekerasan (Hardness)', 'C. Belahan (Cleavage)', 'D. Warna (Color)'],
    correct_answer='B. Kekerasan (Hardness)'
)

# Pertanyaan 3: Belahan vs. Pecahan
my_quiz.add_question(
    question='Kecenderungan mineral untuk pecah di sepanjang bidang datar yang rata disebut...',
    choices=['A. Belahan (Cleavage)', 'B. Pecahan (Fracture)', 'C. Goresan (Streak)', 'D. Bentuk Kristal (Crystal Form)'],
    correct_answer='A. Belahan (Cleavage)'
)

# Pertanyaan 4: Kilap Mineral
my_quiz.add_question(
    question='Istilah yang digunakan untuk menggambarkan bagaimana permukaan mineral memantulkan cahaya adalah...',
    choices=['A. Densitas', 'B. Kekerasan', 'C. Kilap (Luster)', 'D. Transparansi'],
    correct_answer='C. Kilap (Luster)'
)

# Pertanyaan 5: Kelompok Mineral Paling Umum
my_quiz.add_question(
    question='Kelompok mineral yang paling melimpah di kerak bumi adalah...',
    choices=['A. Karbonat', 'B. Oksida', 'C. Sulfida', 'D. Silikat'],
    correct_answer='D. Silikat'
)

# Pertanyaan 6: Perbedaan Mineral dan Batuan
my_quiz.add_question(
    question='Apa perbedaan mendasar antara mineral dan batuan?',
    choices=['A. Mineral lebih keras daripada batuan.', 'B. Batuan adalah agregat dari satu atau lebih mineral.', 'C. Mineral hanya ditemukan di dalam gunung berapi.', 'D. Batuan memiliki warna yang lebih gelap daripada mineral.'],
    correct_answer='B. Batuan adalah agregat dari satu atau lebih mineral.'
)

# Pertanyaan 7: Bentuk Kristal
my_quiz.add_question(
    question='Bentuk geometris eksternal dari sebuah mineral, yang merupakan ekspresi dari susunan atom internalnya yang teratur, disebut...',
    choices=['A. Tekstur', 'B. Struktur', 'C. Bentuk Kristal (Crystal Form)', 'D. Komposisi'],
    correct_answer='C. Bentuk Kristal (Crystal Form)'
)

# Pertanyaan 8: Contoh Mineral (Halit)
my_quiz.add_question(
    question='Mineral Halit (Halite) secara kimiawi dikenal sebagai Natrium Klorida (NaCl) dan umum digunakan sebagai...',
    choices=['A. Bahan bangunan', 'B. Sumber logam besi', 'C. Garam dapur', 'D. Permata'],
    correct_answer='C. Garam dapur'
)

# Pertanyaan 9: Mineral Terkeras
my_quiz.add_question(
    question='Mineral apakah yang menempati peringkat 10 pada skala Mohs dan dikenal sebagai mineral alami terkeras?',
    choices=['A. Kuarsa', 'B. Topaz', 'C. Intan', 'D. Korundum'],
    correct_answer='C. Intan'
)

# Pertanyaan 10: Unit Dasar Silikat
my_quiz.add_question(
    question='Unit dasar penyusun semua mineral silikat adalah...',
    choices=['A. Karbonat tetrahedron (CO₃)', 'B. Silika tetrahedron (SiO₄)', 'C. Oksida oktahedron (O₆)', 'D. Sulfat piramida (SO₄)'],
    correct_answer='B. Silika tetrahedron (SiO₄)'
)

print('Welcome to the interactive quiz builder!')
my_quiz.take_quiz()