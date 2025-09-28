person = {
    "name": "John",
    "age": 36,
    "country": "Norway"
}

# Add new key-value pair
person["city"] = "Oslo"

# Update value
person["age"] = 37

# Remove key-value pair
if "city" in person:
    del person["city"]

print(person)