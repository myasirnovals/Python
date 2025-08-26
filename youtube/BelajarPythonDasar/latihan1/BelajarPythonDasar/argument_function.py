'''Fungsi dengan argument (input)'''


# Template
# def nama_fungsi(argument)
#       Badan fungsi


def hello_wrold(nama):
    '''fungsi hello world menerima input dengan variable nama'''
    print(f"Selamat datang dunia wahai {nama}")


hello_wrold("Westbrook")


# program tambah
def tambah(angka_1, angka_2):
    '''fungsi tambah'''
    hasil = angka_1 + angka_2
    print(f"{angka_1} + {angka_2} = {hasil}")


tambah(1, 5)


def say_hi(list_studio):
    '''fungsi say hi'''
    data_studio = list_studio.copy()
    for studio in data_studio:
        print(f"Yang terhormat {studio}")


studio_anime = [
    "White Fox", "J.C. Staff", "Kyoto Animation", "Clover Work", "A-1 Pictures", "Showgate", "COmix Wave", "Key-Studio"
]

say_hi(studio_anime)