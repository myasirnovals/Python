# program list buku

list_buku = []

while True:
    print("\nMasukan data buku")
    judul = input("judul buku\t: ")
    penulis = input("nama penulis\t: ")

    buku_baru = [judul, penulis]
    list_buku.append(buku_baru)

    print("\n\n","=" * 10, "Data Buku", "=" * 10)
    print("No.\t| judul\t\t\t\t| Penulis")
    for index, buku in enumerate(list_buku):
        print(f"{index + 1}\t| {buku[0]}\t\t| {buku[1]}")

    print("\n\n", "=" * 20)
    isLanjut = input("Apakah dilanjutkan? (y/n) : ")

    if isLanjut == "n":
        break

print("PROGRAM SELESAI")