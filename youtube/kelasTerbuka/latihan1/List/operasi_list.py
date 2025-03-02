data_angka = [1, 1, 2, 1, 2, 3, 1, 2, 3, 4, 1, 2, 3, 4, 5]

print(f"data angka = \n{data_angka}")

# count data
jumlah_angka_1 = data_angka.count(1)
jumlah_angka_2 = data_angka.count(2)
print(f"jumlah huruf a = {jumlah_angka_1}")
print(f"jumlah huruf n = {jumlah_angka_2}")

# ambil posisi data
print("\n")
data = ["Zhongli", "Raiden", "Nahida", "Venti", "Focalor"]

print(f"data jajaran para archon = \n{data}")

index_venti = data.index("Venti")

print(f"index Archon anemo = {index_venti}")

# mengurutkan list
print("\n")
print(f"data angka sebelum di sort = \n{data_angka}")
data_angka.sort()
print(f"data angka setelah di sort = \n{data_angka}")

# membalikan list setelah di sort/urut kan terlebih dahulu
data_angka.reverse()
print(f"data angka di sort secara descending = \n{data_angka}")