import random
import string

word_length = 18
components = [string.ascii_letters, string.digits, '!@#$%^&*()_-+=']
chars = []

for clist in components:
    for item in clist:
        chars.append(item)


def generate_password():
    password = []

    for i in range(word_length):
        random_char = random.choice(chars)
        password.append(random_char)

    return ''.join(password)


print(generate_password())