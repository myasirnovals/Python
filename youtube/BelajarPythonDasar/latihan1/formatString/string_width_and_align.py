# Width and Multiline

# Data

data_nama = "Ucup Surucup"
data_umur = 17
data_tinggi = 150.1
data_nomor_sepatu = 44

# string standard
data_string = f"nama = {data_nama}, umur = {data_umur}, " \
              f"tinggi = {data_tinggi}, sepatu = {data_nomor_sepatu}"

print(5 * "=" + "Data String" + 5 * "=")
print(data_string)

# string multiline (dengan menggunakan enter atau new line, \n)
data_string = f"nama = {data_nama}, \numur = {data_umur}, " \
              f"\ntinggi = {data_tinggi}, \nsepatu = {data_nomor_sepatu}"

print("\n" + 5 * "=" + "Data String" + 5 * "=")
print(data_string)

# string multiline (kutip triplets)
judul = "\n" + 5 * "=" + "Data String" + 5 * "="

data_string = f"""{judul}
nama \t= {data_nama}
umur \t= {data_umur}
tinggi \t= {data_tinggi}
sepatu \t= {data_nomor_sepatu}
"""

print(data_string)

# mengatur lebar
data_nama = "Ucup Surucup"

data_string = f"""{judul}
nama   = {data_nama:>5}
umur   = {data_umur:>5}
tinggi = {data_tinggi:5}
sepatu = {data_nomor_sepatu:5}
"""

print(data_string)
