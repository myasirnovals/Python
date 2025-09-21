def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b != 0:
        return a / b
    else:
        return "Cannot divide by zero"

while True:
    print("\nMenu:")
    print("1. Add")
    print("2. Subtract")
    print("3. Multiply")
    print("4. Divide")
    print("5. Exit")

    choice = input("Enter your choice (1/2/3/4/5): ")

    if choice == "5":
        print("Exiting the program...")
        break

    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))

    if choice == "1":
        print(f"Result: {num1} + {num2} = {add(num1, num2)}")
    elif choice == "2":
        print(f"Result: {num1} - {num2} = {subtract(num1, num2)}")
    elif choice == "3":
        print(f"Result: {num1} * {num2} = {multiply(num1, num2)}")
    elif choice == "4":
        print(f"Result: {num1} / {num2} = {divide(num1, num2)}")
    else:
        print("Invalid choice. Please enter a valid choice.")