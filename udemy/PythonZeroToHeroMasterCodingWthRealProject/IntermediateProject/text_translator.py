from deep_translator import GoogleTranslator


def text_translate(text, lang):
    translated = GoogleTranslator(source='auto', target=lang)
    result = translated.translate(text)
    print(result)

text_translate(input('Enter your text: '), input('Enter the language: '))
