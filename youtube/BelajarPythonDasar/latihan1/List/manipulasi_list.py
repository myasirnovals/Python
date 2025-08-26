## Operasi

data = ["Zhongli", "Raiden", "Venti"]

# mengambil data dari list
print(f"data pertama (index 0) = {data[0]}")
print(f"data pertama (index 1) = {data[1]}")
print(f"data pertama (index 2) = {data[2]}")

# mengambil info jumlah data dalam list
panjang_data = len(data)
print(f"panjang data = {panjang_data}")

## memanipulasi data list

# menambahkan item pada list sesuai posisi
print(f"data sebelum diubah = \n{data}")

data.insert(1, "Nahida")
print(f"data sesudah di tambah = \n{data}")

# menambah di akhir list
data.append("Focalor")
print(f"data ditambah lagi = \n{data}")

# menambah list dengan list
data_baru = ["Kontrak", "Kebijaksanaan", "Keabadian", "Kebebasan", "Keadilan"]
data.extend(data_baru)
print(f"data gabungan = \n{data}")

# merubah data
data[0] = "Morax"
data[1] = "Lesser Lord Kusanali"
data[2] = "Raiden Shogun"
data[3] = "Barbatos"

print(f"merubah data = \n{data}")

# menghapus data
data.remove("Focalor")
print(f"Menghapus 'Focalor' dari jajaran Archon = \n{data}")

# menghapus data yang berada di akhir list
data.pop()
print(f"Menghapus idealisme 'Keadilan' dari jajaran idealisme Archon = \n{data}")