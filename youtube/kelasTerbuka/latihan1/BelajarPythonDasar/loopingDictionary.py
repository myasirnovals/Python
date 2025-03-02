# looping dictionary

teman_teman = {
    "kontrak": "Zhongli",
    "keabadian": "Raiden Ei",
    "kebijaksanaan": "Nahida",
    "kebebasan": "Venti",
    "keadilan": "Furina"
}

# looping first try (yang keluar adalah key)

for teman in teman_teman:
    print(teman)

# operator untuk mengambil item / iterables
keys = teman_teman.keys()
print(keys)

for key in teman_teman.keys():
    print(teman_teman.get(key))

values = teman_teman.values()
print(values)

for value in teman_teman.values():
    print(value)

items = teman_teman.items()
print(items)

for item in teman_teman.items():
    print(item)

for key, value in teman_teman.items():
    print(f"Idealisme = {key}, Archon = {value}")