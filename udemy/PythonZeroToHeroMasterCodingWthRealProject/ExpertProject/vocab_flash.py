class VocabularyFlashcard:
    def __init__(self):
        self.flashcards = {}

    def add_flashcard(self, word, meaning):
        self.flashcards[word] = meaning

    def quiz(self):
        if not self.flashcards:
            print('No flashcards available!. please add some flashcards first!')
            return

        print('Starting vocabulary quiz...')

        for word, meaning in self.flashcards.items():
            user_input = input(f'What does "{word}" means? enter your answer: ').strip().lower()
            if user_input == meaning.lower:
                print('Correct!')
            else:
                print(f'Wrong! The correct answer is {meaning}')

    def review_flashcards(self):
        if not self.flashcards:
            print('No flashcards available!, please add some flashcards first!')
            return

        print('Reviewing vocabulary flashcards: ')
        for word, meaning in self.flashcards.items():
            print(f'word: {word}, meaning: {meaning}')


flashcard_app = VocabularyFlashcard()
flashcard_app.add_flashcard('Galaxy', 'A massive system of stars, gas, dust, and dark matter, bound together by gravity.')
flashcard_app.add_flashcard('Nebula', 'A giant interstellar cloud of dust and gas, where new stars are formed.')
flashcard_app.add_flashcard('Light-Year', 'A unit of distance equal to the distance that light travels in one year in a vacuum.')
flashcard_app.add_flashcard('Black Hole', 'A region in space with gravity so strong that nothing, not even light, can escape from it.')
flashcard_app.add_flashcard('Asteroid', 'A small, rocky celestial body that orbits the Sun, mostly found between Mars and Jupiter.')
flashcard_app.add_flashcard('Comet', 'A celestial body made of ice, dust, and rock that forms a tail as it approaches the Sun.')
flashcard_app.add_flashcard('Supernova', 'A very powerful and brilliant stellar explosion, marking the end of a massive star\'s life cycle.')
flashcard_app.add_flashcard('Orbit', 'The curved path that a celestial object takes around another object due to the influence of gravity.')
flashcard_app.add_flashcard('Solar System', 'The system consisting of the Sun and all objects bound to it by gravity, including planets and moons.')
flashcard_app.add_flashcard('Eclipse', 'An event where one celestial object is obscured by another passing in front of it, such as a solar or lunar eclipse.')
