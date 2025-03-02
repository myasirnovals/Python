# continue, pass

# pass -> dia berfungsi sebagai dummy, tidak akan dieksekusi

# angka = 0
#
# while angka < 5:
#     angka += 1
#
#     if angka == 3:
#         pass
#
#     print(angka)

# Continue
angka = 0
print(f"Angka sekarang -> {angka}")

while angka < 5:
    angka += 1

    if angka == 3:
        continue
        
    print(f"Angka sekarang -> {angka}")

print("Akhir dari program")
