## --- LIST ---

# kumpulan data numbers
data_angka = [1, 2, 3]
print(data_angka)

# kumpulan data string
data_string = ["Dietfried", "Gilbert", "Claudia"]
print(data_string)

# kumpulan data boolean
data_boolean = [True, False, True, True]
print(data_boolean)

# kumpulan data campuran
data_campuran = ["Koe no Katachi", 8.9, True]
print(data_campuran)

## cara alternatif membuat list
data_range = range(0, 10)
print(data_range)
data_list = list(data_range)
print(data_list)

# membuat list dengan for loop, list comprehension
list_pake_for = [i ** 2 for i in range(0, 10)]
print(list_pake_for)

# membuat list dengan for loop + if statement
list_pake_for_if_genap = [i for i in range(0, 10) if i % 2 == 0]
print(list_pake_for_if_genap)

list_pake_for_if_ganjil = [i for i in range(0, 10) if i % 2 != 0]
print(list_pake_for_if_ganjil)
