''' Latihan fungsi '''

import os


# program menghitung luas dan keliling persegi panjang

# membuat header program
def header():
    ''' Fungsi untuk membuat header '''
    os.system("clear")

    print(f"{'-' * 40:^40}")
    print(f"|{'PROGRAM MENGHITUNG LUAS':^38}|")
    print(f"|{'DAN KELILING PERSEGI PANJANG':^38}|")
    print(f"{'-' * 40:^40}")


# mengambil input user
def input_user():
    ''' Fungsi untuk input user '''
    lebar = int(input("Masukan Nilai: "))
    panjang = int(input("Masukan Nilai: "))

    return lebar, panjang


# program menghitung luas dan keliling
def hitung_luas(lebar, panjang):
    ''' Fungsi untuk menghitung luas '''
    return panjang * lebar


def hitung_keliling(lebar, panjang):
    ''' Fungsi untuk menghitung keliling '''
    return 2 * (panjang + lebar)


def display(message, value):
    ''' Fungsi untuk menampilkan pesan '''
    print(f"Hasil perhitungan {message} = {value}")


while True:
    header()

    LEBAR, PANJANG = input_user()
    LUAS = hitung_luas(PANJANG, LEBAR)
    KELILING = hitung_keliling(PANJANG, LEBAR)

    # tampilkan hasilnya
    display("luas", LUAS)
    display("keliling", KELILING)

    isContinue = input("apakah lanjut (y/N): ")
    if isContinue == "n" or isContinue == "N":
        break

print("Progrm selsai, terimakasih")
