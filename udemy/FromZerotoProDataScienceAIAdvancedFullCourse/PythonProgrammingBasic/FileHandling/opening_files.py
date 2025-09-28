with open("sample.txt", "r") as file:
    content = file.readlines()
    print(content)

with open("sample.txt", "w") as file:
    file.write("Hello World!")
    file.writelines(["Hello", "World"])

# File is automatically closed
try:
    with open("sample.txt", "r") as file:
        content = file.read()
except FileNotFoundError:
    print("File not found")
