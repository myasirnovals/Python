# latihan

# kalkulator sederhana
print(20 * "=")
print("KALKULATOR SEDERHANA")
print(20 * "=" + "\n")

angka_1 = float(input("Masukan angka 1 = "))
operasi = input("operator (+,-,*,/) : ")
angka_2 = float(input("Masukan angka 2 = "))

# percabangannya
if operasi == "+":
    hasil = angka_1 + angka_2
    print(f"Hasilnya adalah {hasil}")
elif operasi == "-":
    hasil = angka_1 - angka_2
    print(f"Hasilnya adalah {hasil}")
elif operasi == "*":
    hasil = angka_1 * angka_2
    print(f"Hasilnya adalah {hasil}")
elif operasi == "/":
    hasil = angka_1 / angka_2
    print(f"Hasilnya adalah {hasil}")
else:
    print("Operator yang Anda masukan salah")

print("Akhir dari program")
