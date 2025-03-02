# copy dictionary

teman_teman = {
    "kontrak": "Morax",
    "keabadian": "Raiden Shogun",
    "kebijaksanaan": "Lesser Lord Kusanali",
    "kebebasan": "Barbatos",
    "keadilan": "Focalor"
}

friends = teman_teman.copy()

print(f"\nteman_teman: {teman_teman}\n")
print(f"firends: {friends}")

teman_teman["kontrak"] = "Zhongli"
print(f"\nteman_teman: {teman_teman}\n")
print(f"firends: {friends}")

# pop dictionary (berdasarkan key)
dataIdealisme = friends.pop("kebebasan")
print(f"data idealisme = {dataIdealisme}")
print(f"friends = {friends}\n")

# pop item dictionary (berdasarkan data terakhir)
dataTerakhir = friends.popitem()
print(f"data terakhir = {dataTerakhir}")
print(f"friends = {friends}\n")