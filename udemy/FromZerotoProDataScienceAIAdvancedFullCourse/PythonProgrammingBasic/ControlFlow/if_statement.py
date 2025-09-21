# Example 1: Checking a condition
num = 10
if num > 0:
    print("num is positive")
elif num == 0:
    print("num is equal to 0")
else:
    print("num is negative")

# Example 2: Nested condition
age = 25
if age > 18:
    if age < 30:
        print("Young Adult")
    else:
        print("Adult")
else:
    print("Child")