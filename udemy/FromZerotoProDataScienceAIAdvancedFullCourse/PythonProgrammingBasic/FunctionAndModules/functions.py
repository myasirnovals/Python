# def function_name(parameters):
#     TODO Something

# Import keyword
import math as m
print(m.sqrt(16))

# Function with parameters and return value
def add_numbers(a, b):
    return a + b

result = add_numbers(1, 2)
print(f"Sum: {result}")

# Local Scope
def greet():
    message = "Hello World!"
    print(message)

greet()
# print(message) # Error: message is not defined in global scope

# Global Scope
greeting = "Hello World!"

def say_hello():
    print(greeting + " from inside the function")

say_hello()
print(greeting + " from outside the function")