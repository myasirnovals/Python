# Syntax for for-loop
# for <variable> in <iterable>:
#     <statements>

# Loop through a list
fruits = ['banana', 'apple', 'mango']
for fruit in fruits:
    print(fruit)

# Loop with a range function
for i in range(5):
    print(i)

# Syntax for while-loop
# while <condition>:
#     <statements>

# Count down from 5
count = 5
while count > 0:
    print(count)
    count -= 1

print("Outside While Loop")

# Break keyword
for i in range(10):
    if i == 5:
        break
    print(i)

print("Outside For Loop")

# Continue keyword
for i in range(10):
    if i == 5:
        continue
    print(i)

print("Outside For Loop")

for i in range(10):
    if i % 2 == 0:
        continue
    print(i)
    
print("Outside For Loop")
