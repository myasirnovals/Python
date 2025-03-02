# latihan perulangan membuat segitiga

sisi = 10

# 1. Menggunakan For

# dummy variable
count = 1
for i in range(sisi):
    print("*" * count)
    count += 1

# 2. Menggunakan while

count = 1
while True:
    print("*" * count)
    count += 1

    if count > sisi:
        break

# 3. Hanaya Ganjil Saja

count = 1
while True:
    if count % 2 == 0:
        count += 1
        continue

    print("*" * count)
    count += 1

    if count > sisi:
        break

# $. Segitiga sama kaki

count = 1
spasi = int(sisi / 2)

while True:
    if (count % 2):
        print("" * spasi, "+" * count)
        spasi -= 1
        count += 1
    else:
        count += 1
        continue

    if count > sisi:
        break
