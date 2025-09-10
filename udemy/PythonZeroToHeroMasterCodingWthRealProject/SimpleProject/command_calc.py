import os


def addition():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Addition')

    continue_calc = 'y'

    num1 = float(input('enter a number 1: '))
    num2 = float(input('enter a number 2: '))
    ans = num1 + num2
    values_entered = 2
    print(f'current result: {ans}')

    while continue_calc.lower() == 'y':
        continue_calc = input('Enter more (y/n): ')
        while continue_calc.lower() not in ['y', 'n']:
            print('Please enter \'y\' or \'n\'')
            continue_calc = input('Enter more (y/n): ')
        if continue_calc.lower() == 'n':
            break
        num = float(input('Enter another number: '))
        ans += num
        print(f'current result: {ans}')
        values_entered += 1
    return [ans, values_entered]


def subtraction():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Subtraction')

    continue_calc = 'y'

    num1 = float(input('enter a number 1: '))
    num2 = float(input('enter a number 2: '))
    ans = num1 - num2
    values_entered = 2
    print(f'current result: {ans}')

    while continue_calc.lower() == 'y':
        continue_calc = input('Enter more (y/n): ')
        while continue_calc.lower() not in ['y', 'n']:
            print('Please enter \'y\' or \'n\'')
            continue_calc = input('Enter more (y/n): ')
        if continue_calc.lower() == 'n':
            break
        num = float(input('Enter another number: '))
        ans -= num
        print(f'current result: {ans}')
        values_entered += 1
    return [ans, values_entered]


def multiplication():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Multiplication')

    continue_calc = 'y'

    num1 = float(input('enter a number 1: '))
    num2 = float(input('enter a number 2: '))
    ans = num1 * num2
    values_entered = 2
    print(f'current result: {ans}')

    while continue_calc.lower() == 'y':
        continue_calc = input('Enter more (y/n): ')
        while continue_calc.lower() not in ['y', 'n']:
            print('Please enter \'y\' or \'n\'')
            continue_calc = input('Enter more (y/n): ')
        if continue_calc.lower() == 'n':
            break
        num = float(input('Enter another number: '))
        ans *= num
        print(f'current result: {ans}')
        values_entered += 1
    return [ans, values_entered]


def division():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Division')

    continue_calc = 'y'

    num1 = float(input('enter a number 1: '))
    try:
        num2 = float(input('enter a number 2: '))
        if num2 == 0:
            print('Can\'t divide by zero!')
            return division()
    except ValueError:
        print('Invalid input! Please enter a number.')
        return division()
    ans = num1 / num2
    values_entered = 2
    print(f'current result: {ans}')

    while continue_calc.lower() == 'y':
        continue_calc = input('Enter more (y/n): ')
        while continue_calc.lower() not in ['y', 'n']:
            print('Please enter \'y\' or \'n\'')
            continue_calc = input('Enter more (y/n): ')
        if continue_calc.lower() == 'n':
            break

        while True:
            try:
                num = float(input('Enter another number: '))
                if num == 0:
                    print('Can\'t divide by zero!')
                    continue
                break
            except ValueError:
                print('Invalid input! Please enter a number.')

        ans /= num
        print(f'current result: {ans}')
        values_entered += 1
    return [ans, values_entered]


def calculator():
    quit = False
    while not quit:
        results = []
        print("simple calculator in python!")
        print("Enter \'a\' for addition")
        print("Enter \'s\' for subtraction")
        print("Enter \'m\' for multiplication")
        print("Enter \'d\' for division")
        print("Enter \'q\' to quit")
        choice = input("Enter your choice: ")
        while choice.lower() not in ['a', 's', 'm', 'd', 'q']:
            print("Please enter a valid choice!")
            choice = input("Enter your choice: ")
        if choice.lower() == 'q':
            quit = True
            continue
        elif choice.lower() == 'a':
            results = addition()
            print('Answer = ', results[0], ' total input ', results[1])
        elif choice.lower() == 's':
            results = subtraction()
            print('Answer = ', results[0], ' total input ', results[1])
        elif choice.lower() == 'm':
            results = multiplication()
            print('Answer = ', results[0], ' total input ', results[1])
        elif choice.lower() == 'd':
            results = division()
            print('Answer = ', results[0], ' total input ', results[1])

if __name__ == '__main__':
    calculator()