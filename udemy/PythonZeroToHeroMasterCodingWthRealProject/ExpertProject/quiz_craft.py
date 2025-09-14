import tkinter as tk
from tkinter import messagebox


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Modern Quiz Game')
        self.question = [
            {
                'question': 'Apakah pusat dari Tata Surya kita?',
                'choices': ['A. Bumi', 'B. Jupiter', 'C. Matahari', 'D. Bulan'],
                'correct_answer': 'C. Matahari'
            },
            {
                'question': 'Planet manakah yang terbesar di Tata Surya?',
                'choices': ['A. Saturnus', 'B. Jupiter', 'C. Uranus', 'D. Bumi'],
                'correct_answer': 'B. Jupiter'
            },
            {
                'question': 'Planet manakah yang sering dijuluki sebagai "Planet Merah"?',
                'choices': ['A. Venus', 'B. Mars', 'C. Merkurius', 'D. Jupiter'],
                'correct_answer': 'B. Mars'
            },
            {
                'question': 'Kumpulan masif dari bintang, gas, debu, dan materi gelap yang terikat oleh gravitasi disebut...',
                'choices': ['A. Nebula', 'B. Tata Surya', 'C. Galaksi', 'D. Asteroid'],
                'correct_answer': 'C. Galaksi'
            },
            {
                'question': 'Apa nama galaksi tempat Tata Surya kita berada?',
                'choices': ['A. Andromeda', 'B. Triangulum', 'C. Bima Sakti (Milky Way)', 'D. Sombrero'],
                'correct_answer': 'C. Bima Sakti (Milky Way)'
            },
            {
                'question': '"Tahun cahaya" (light-year) adalah satuan yang digunakan untuk mengukur...',
                'choices': ['A. Waktu', 'B. Jarak', 'C. Kecerahan', 'D. Kecepatan'],
                'correct_answer': 'B. Jarak'
            },
            {
                'question': 'Gaya fundamental apakah yang menahan planet-planet tetap pada orbitnya mengelilingi Matahari?',
                'choices': ['A. Gaya Magnet', 'B. Gaya Nuklir Lemah', 'C. Gaya Gravitasi', 'D. Gaya Elektromagnetik'],
                'correct_answer': 'C. Gaya Gravitasi'
            },
            {
                'question': 'Fase bulan saat Bulan berada di antara Bumi dan Matahari, sehingga tidak terlihat dari Bumi, disebut...',
                'choices': ['A. Bulan Purnama', 'B. Bulan Sabit', 'C. Bulan Baru', 'D. Bulan Kuartal Pertama'],
                'correct_answer': 'C. Bulan Baru'
            },
            {
                'question': 'Planet manakah yang paling terkenal dengan sistem cincinnya yang menonjol?',
                'choices': ['A. Jupiter', 'B. Uranus', 'C. Neptunus', 'D. Saturnus'],
                'correct_answer': 'D. Saturnus'
            },
            {
                'question': 'Apa penyebab utama terjadinya pergantian musim di Bumi?',
                'choices': ['A. Jarak Bumi dari Matahari', 'B. Kemiringan sumbu rotasi Bumi',
                            'C. Kecepatan rotasi Bumi', 'D. Aktivitas bintik matahari'],
                'correct_answer': 'B. Kemiringan sumbu rotasi Bumi'
            }
        ]

        self.question_index = 0
        self.score = 0

        self.question_label = tk.Label(root, text='', font=('Arial', 14))
        self.question_label.pack(pady=20)

        self.radio_var = tk.StringVar()
        self.choices = []

        for i in range(4):
            choice = tk.Radiobutton(root, text='', variable=self.radio_var, value=i, font=('Arial', 12))
            choice.pack(pady=10, anchor='w')
            self.choices.append(choice)

        self.next_button = tk.Button(root, text='Next', command=self.next_question, font=('Arial', 12), bg='#4caf50',
                                     fg='white')
        self.next_button.pack(pady=20)
        self.display_question()

    def display_question(self):
        if self.question_index < len(self.question):
            question_data = self.question[self.question_index]
            self.question_label.config(text=question_data['question'])

            for i, choice in enumerate(self.choices):
                choice.config(text=question_data['choices'][i])

            self.radio_var.set(-1)
        else:
            self.show_result()

    def next_question(self):
        selected_choice = self.radio_var.get()

        if selected_choice == '-1':
            messagebox.showwarning('Warning', 'Pilih pilihan terlebih dahulu!')
        else:
            select_choice_index = int(selected_choice)

            if self.question[self.question_index]['choices'][select_choice_index] == self.question[self.question_index][
                'correct_answer']:
                self.score += 1

            self.question_index += 1
            self.display_question()

    def show_result(self):
        messagebox.showinfo('Quiz Result', f'Score: {self.score}/{len(self.question)}')
        self.root.destroy()

def main():
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
