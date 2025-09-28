def is_palindrome(word):
    text = "".join(char.lower() for char in word if char.isalnum())
    return text == text[::-1]

input_text = input("Enter a word: ")

if is_palindrome(input_text):
    print(f"'{input_text}' is a palindrome.")
else:
    print(f"'{input_text}' is not a palindrome.")