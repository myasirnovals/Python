numbers1 = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 1, 2, 3, 4}

empty_set = set()

print(numbers1)

numbers1.add(5)

print(numbers1)

numbers2 = {1, 2, 3, 4, 5, 11, 12, 13, 14, 15}

# Union
print(numbers1 | numbers2)

# Intersection
print(numbers1 & numbers2)

# Difference
print(numbers1 - numbers2)
