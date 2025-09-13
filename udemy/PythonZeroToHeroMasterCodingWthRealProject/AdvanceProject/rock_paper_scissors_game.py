import random
import os
import re


def check_play_status():
    valid_responses = ['yes', 'no', 'y', 'n', ]

    while True:
        try:
            response = input('Do you want to play a game of Rock Paper Scissors? (yes/no) ')
            response = response.lower()

            if response not in valid_responses:
                raise ValueError('Please enter yes or no')

            if response in ['yes', 'y']:
                return True
            else:
                os.system('cls' if os.name == 'nt' else 'clear')
                print('Thanks for playing!')
                exit()
        except ValueError as e:
            print(f'Error: {e}')


def play_rps():
    play = True

    while play:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('')
        print('Rock, Paper, Scissors Game')

        user_choice = input('choose your weapon \n[R]ock, [P]aper, [S]cissors: ')
        user_choice = user_choice.upper()

        if not re.match('[SsRrPp]', user_choice):
            print('Please choose a letter: ')
            print('[R]ock, [P]aper, [S]cissors')
            continue

        print(f'You chose {user_choice}')

        choices = ['R', 'P', 'S']
        app_choice = random.choice(choices)

        print(f'Computer chose: {app_choice}')

        if app_choice == user_choice:
            print('It\'s a tie!')
            play = check_play_status()
        elif app_choice == 'R' and user_choice == 'S':
            print('Rock beats scissors! Computer win!')
            play = check_play_status()
        elif app_choice == 'P' and user_choice == 'R':
            print('Paper beats rock! Computer win!')
            play = check_play_status()
        elif app_choice == 'S' and user_choice == 'P':
            print('Scissors beats paper! Computer win!')
            play = check_play_status()
        else:
            print('You Win!\n')
            play = check_play_status()

if __name__ == '__main__':
    play_rps()
