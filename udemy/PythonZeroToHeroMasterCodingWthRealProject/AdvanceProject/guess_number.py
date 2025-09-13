import random

attempts_list = []


def show_score():
    if not attempts_list:
        print('There are no high score it is all yours!')
    else:
        print(f'The current high score is: {max(attempts_list)}')


def start_game():
    attempts = 0
    rand_num = random.randint(1, 100)
    print('Hello travel!, welcome to the game of guessing')
    player_name = input('What is your name? ')
    wanna_play = input(f'Hi {player_name}, do you want to play? (yes/no) ')

    if wanna_play.lower() != 'yes':
        print('thats cool thanks')
        exit()
    else:
        show_score()

    while wanna_play.lower() == 'yes':
        try:
            guess = int(input('pick a number between 1 and 100: '))

            if guess < 1 or guess > 100:
                raise ValueError('please enter a number between 1 and 100')

            attempts += 1
            attempts_list.append(attempts)

            if guess == rand_num:
                print('nice you got it right!')
                print(f'it took you {attempts} attempts')

                wanna_play = input('do you want to play again? (yes/no) ')

                if wanna_play.lower() != 'yes':
                    print('thanks for playing')
                    break
                else:
                    attempts = 0
                    rand_num = random.randint(1, 100)
                    show_score()
                    continue
            else:
                if guess > rand_num:
                    print('too higher')
                elif guess < rand_num:
                    print('too lower')
        except ValueError as e:
            print('please enter a valid number')
            print(e)


if __name__ == '__main__':
    start_game()