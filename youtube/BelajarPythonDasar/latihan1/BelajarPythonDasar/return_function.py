''' Fungsi dengan kembalian '''


# template fungsi dengan kembalian
# def nama_fungsi(argument)
#       badan fungsi
#       return output

# fungsi kuadrat

def kuadrat(input_angka):
    ''' Fungsi Kuadrat '''
    output_kuadrat = input_angka ** 2
    return output_kuadrat


y = kuadrat(5)
print(y)

print(kuadrat(6))

z = 10 + kuadrat(7)
print(z)


# fungsi tambah

def tambah(angka_1, angka_2):
    return angka_1 + angka_2


a = tambah(10, 8)
print(a)


def operasi_matematika(angka_1, operator, angka_2):
    if operator == '+':
        hasil = angka_1 + angka_2
    elif operator == '-':
        hasil = angka_1 - angka_2
    elif operator == '*':
        hasil = angka_1 * angka_2
    elif operator == '/':
        hasil = angka_1 / angka_2
    elif operator == '%':
        hasil = angka_1 % angka_2
    else:
        hasil = 0

    return hasil


hasil = operasi_matematika(2, '*', 3)
print(hasil)
