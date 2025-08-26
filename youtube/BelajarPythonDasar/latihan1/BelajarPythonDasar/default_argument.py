''' Default Argument '''


# def fungsi(argument):
# def fungsi(argument = nilai defaultnya)

# contoh 1
def say_hello(name='Anonymous'):
    ''' fungsi dengan default argument '''
    print(f"Hallo {name}")


say_hello("Sirosaki Hina")
say_hello()


# contoh 2
def sapa_dia(nama, pesan='dari club apa?'):
    ''' fungsi dengan satu input biasa, dan satu input default '''
    print(f"Hai {nama}, {pesan}")


sapa_dia("Hina", "Selamat datang di Perfect Team")
sapa_dia("Shiroko")


# contoh 3
def hitung_pangkat(angka, pangkat):
    hasil = angka ** pangkat

    return hasil


print(hitung_pangkat(2, 4))

result = hitung_pangkat(pangkat=2, angka=5)
print(result)


# contoh 4
def fungsi(input1=1, input2=2, input3=3, input4=4):
    hasil = input1 + input2 + input3 + input4

    return hasil


print(fungsi())
print(fungsi(input3=10))
