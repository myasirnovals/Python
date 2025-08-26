data_0 = [1, 2]
data_1 = [3, 4]

data_2d = [data_0, data_1]
data_2d_copy = data_2d.copy()

print(f"data = {data_2d}")
print(f"data copy = {data_2d_copy}")

# mengambil data 

data = data_2d[0][0]
print(f"data = {data}")

# address semua list

print(f"address asli = {hex(id(data_2d))}")
print(f"address copy = {hex(id(data_2d_copy))}")

print("address dari member ke-1")
print(f"address asli = {hex(id(data_2d[0]))}")
print(f"address copy = {hex(id(data_2d_copy[0]))}")

data_2d[1][0] = 5
print(f"asli = {data_2d}")
print(f"copy = {data_2d_copy}")

# kita gunakan deepcopy

from copy import deepcopy

data_2d = [data_0, data_1, 10]
data_2d_deepcopy = deepcopy(data_2d)

print(f"address asli = {hex(id(data_2d))}")
print(f"address deep = {hex(id(data_2d_deepcopy))}")

print("address dari member ke-1")
print(f"address asli = {hex(id(data_2d[0]))}")
print(f"address copy = {hex(id(data_2d_deepcopy[0]))}")

data_2d[1][0] = 30
print(f"asli = {data_2d}")
print(f"copy = {data_2d_copy}")
print(f"deep = {data_2d_deepcopy}")