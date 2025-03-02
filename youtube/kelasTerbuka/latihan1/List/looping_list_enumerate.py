# looping dari list

# for loop
print("\nFor Loop")
kumpulan_angka = [4, 3, 2, 5, 6, 1]

for angka in kumpulan_angka:
    print(f"angka = {angka}")

archon = ["Morax", "Raiden Shogun", "Lesser Lord Kusanali", "Barbatos", "Focalor"]

for dewa in archon:
    print(f"Archon = {dewa}")

# for loop dan range
print("\nFor Loop and Range")
kumpulan_angka = [10, 5, 4, 2, 6, 5]

panjang = len(kumpulan_angka)

for i in range(panjang):
    print(f"angka = {kumpulan_angka[i]}")

# while loop
print("\nWhile Loop")
kumpulan_angka = [10, 5, 4, 2, 6, 5]

panjang = len(kumpulan_angka)
i = 0

while i < panjang:
    print(f"angka = {kumpulan_angka[i]}")
    i += 1

# list comprehension
print("\nList Comprehension")

data = ["Lesser Lord Kusanali", "Kebijaksanaan", True, 10]

[print(f"data = {i}") for i in data]

angka = [10, 5, 4, 2, 6, 5]

angka_kuadrat = [i ** 2 for i in angka]
print(angka_kuadrat)

# enumerate
print("\nEnumerate")
data_list = ["Morax", "Kontrak", True, 2000]

for index, data in enumerate(data_list):
    print(f"index = {index}, data = {data}")