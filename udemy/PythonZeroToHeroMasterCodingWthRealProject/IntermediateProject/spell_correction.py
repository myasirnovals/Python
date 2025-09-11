from textblob import TextBlob

words = [
    'data scence',
    'mahine learnin',
    'artificila intilegence'
]

corrected_words = []

for i in words:
    corrected_words.append(TextBlob(i))

print('Wrong words: ', words)
print('Corrected words are: ')

for i in corrected_words:
    print(i.correct(), end=' ')