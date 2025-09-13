import string
import getpass


def check_password_strength():
    password = getpass.getpass('Enter your password: ')
    strength = 0
    remarks = ''
    lower_count = upper_count = num_count = wspace_count = special_count = 0

    for char in list(password):
        if char in string.ascii_lowercase:
            lower_count += 1
        elif char in string.ascii_uppercase:
            upper_count += 1
        elif char in string.digits:
            num_count += 1
        elif char in string.whitespace:
            wspace_count += 1
        else:
            special_count += 1

    if lower_count >= 1:
        strength += 1

    if upper_count >= 1:
        strength += 1

    if num_count >= 1:
        strength += 1

    if wspace_count >= 1:
        strength += 1

    if special_count >= 1:
        strength += 1

    if strength == 1:
        remarks = 'that is a very weak password \nchange it as soon as possible.'
    elif strength == 2:
        remarks = 'that is a weak password \nchange it as soon as possible.'
    elif strength == 3:
        remarks = 'that is a good password.'
    elif strength == 4:
        remarks = 'that is a strong password.'
    elif strength == 5:
        remarks = 'that is a very strong password.'

    print('Your password has:- ')
    print(f'1. {lower_count} lowercase letters')
    print(f'2. {upper_count} uppercase letters')
    print(f'3. {num_count} digits')
    print(f'4. {wspace_count} whitespaces')
    print(f'5. {special_count} special characters')
    print(f'Your password strength is {strength} and {remarks}')


def check_pwd(another_pw=False):
    while True:
        if another_pw:
            choice = input('Do you want to check another password? (yes/no) ')
        else:
            choice = input('Do you want to check your password? (yes/no) ')

        if choice.lower() == 'yes':
            return True
        elif choice.lower() == 'no':
            return False
        else:
            print('invalid input... please try again.\n')


if __name__ == '__main__':
    print('Welcome to password strength checker')
    check_pass = check_pwd()
    while check_pass:
        check_password_strength()
        check_pass = check_pwd(True)
