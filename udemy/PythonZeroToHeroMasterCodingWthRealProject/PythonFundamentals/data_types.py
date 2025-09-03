# text type: str
x = "hello world"


# numbers type: int, float, complex
int: x = 20
print(x)

float: x = 20.5
print(x)

complex: x = 3 + 5j
print(x)

# sequence type: list, tuple, range
x = [1, 2, 3, 4, 5]
print(x)

tuple: x = (1, 2, 3, 4, "name")
print(x)

x = range(1, 10)
print(x)

# mapping type: dict
x = {"name": "jose", "age": 20}
print(x)

# set type: set, frozenset
x = {1, 2, 3, 4}
print(x)

x = frozenset({1, 2, 3, 4})
print(x)

# boolean type: bool
bool: x = True
print(x)

# binary types: bytes, bytearray, memoryview
x = bytes(5)
print(x)

x = bytearray(5)
print(x)

memoryview(bytes(5))
print(x)

# none type: None
x = None
print(x)