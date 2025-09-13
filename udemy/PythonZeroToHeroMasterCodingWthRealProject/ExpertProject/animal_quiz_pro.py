def check_guess(guess, answer):
    global score
    still_guessing = True
    attempt = 0

    while still_guessing and attempt < 3:
        if guess.lower() == answer.lower():
            print('correct answer!')
            score += 1
            still_guessing = False
        else:
            if attempt < 2:
                guess = input('sorry wrong answer, try again: ')
            attempt += 1

        if attempt == 3:
            print(f'The correct answer was {answer}')

score = 0
print('Guess the animal!')
guess1 = input('which bear lives at the north pole?')
check_guess(guess1, 'polar bear')
guess2 = input('which is the fastest animal?')
check_guess(guess2, 'cheetah')
guess3 = input('which is the larget animal?')
check_guess(guess3, 'blue whale')
print(f'you got {score} out of 3')