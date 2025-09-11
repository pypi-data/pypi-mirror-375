import random
import string

def generate_password(length=12, use_uppercase=True, use_digits=True, use_special=True):
    characters = string.ascii_lowercase
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_digits:
        characters += string.digits
    if use_special:
        characters += string.punctuation

    password = ''.join(random.choice(characters) for _ in range(length))
    return password
