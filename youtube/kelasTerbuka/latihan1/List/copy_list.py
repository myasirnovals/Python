## Teknik menduplikat list

archon = ["Morax", "Raiden Shogun", "Lesser Lord Kusanali", "Barbatos"]
print(f"archon = {archon}")

new_archon = archon
print(f"new_archon = {new_archon}")

# kita akan merubah member dari archon

# ini akan merubah kedua list
archon[1] = "Raiden Ei"
new_archon.sort()

print(f"archon = {archon}")
print(f"new_archon = {new_archon}")

# address dari kedua list
print(f"address archon = {hex(id(archon))}")
print(f"address new_archon = {hex(id(new_archon))}")

# menduplikat list dengan copy

print("membuat list copy_archon dengan archon.copy()")
copy_archon = archon.copy()

print(f"address archon = {hex(id(archon))}")
print(f"address new_archon = {hex(id(new_archon))}")
print(f"address copy_archon = {hex(id(copy_archon))}")

print(f"archon = {archon}")
print(f"new_archon = {new_archon}")
print(f"copy_archon = {copy_archon}")

print("Kita ubah data 0")
copy_archon[0] = "Zhongli"

print(f"archon = {archon}")
print(f"new_archon = {new_archon}")
print(f"copy_archon = {copy_archon}")