student = {
    "name": "John",
    "age": 23,
    "course": "CompSci"
}

student["subject"] = "Math"

print(student)

del student["course"]

print(student)

student.pop("subject")

print(student)

for key, value in student.items():
    print(key, value)
