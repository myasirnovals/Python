# operator dictionary

data_dict = {
    "kontrak": "Morax",
    "keabadian": "Raiden Shogun",
    "kebijaksanaan": "Lesser Lord Kusanali",
    "kebebasan": "Barbatos",
    "keadilan": "Focalor"
}

# panjang dictionary
LENDICT = len(data_dict)

print(f"panjang dictionary: {LENDICT}")

# mengecek key exist atau tidak
KEY = "kontrak"
CHECKKEY = KEY in data_dict
print(f"apakah {KEY} ada di data_dict: {CHECKKEY}")

# mengakses value (read) dengan get
print(data_dict["keabadian"])
print(data_dict.get("keabadian"))
print(data_dict.get("kekuatan", "Key tidak ditemukan")) # cek key dengan message

# mengupdate data
data_dict["kontrak"] = "Zhongli"
print(data_dict)

data_dict["kekuatan"] = "Murata"
print(data_dict)

data_dict.update({"kontrak": "Morax"})
print(data_dict)

# menghapus data pada dictionary
del data_dict["kekuatan"]
print(data_dict)