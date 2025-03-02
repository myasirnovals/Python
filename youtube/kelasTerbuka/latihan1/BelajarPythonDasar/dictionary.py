# list -> array, mengakses dengan menggunakan index

data_list = ["Morax", "Raiden Shogun", "Lesser Lord Kusanali", "Barbatos", "Focalor"]

print(data_list[2])

# dictionary (dict) -> associative array
# identifier -> key

data_dict = {
    "kontrak": "Zhongli",
    "keabadian": "Raiden Ei",
    "kebijaksanaan": "Nahida",
    "kebebasan": "Venti",
    "keadilan": "Furina",
    "archon": data_list
}

print(data_dict['kontrak'])
print(data_dict['archon'])