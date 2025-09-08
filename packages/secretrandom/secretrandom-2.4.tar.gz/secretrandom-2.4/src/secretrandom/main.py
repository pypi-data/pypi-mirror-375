# secretrandom 2.4 - The Cipher Update
import random
import secrets
import string

shuffled_digits_for_unprdictibility = string.digits * 4
SystemRandom = random.SystemRandom()
ver = '''\nsecretrandom 2.4 - \033[3mThe Cipher Update\033[0m
Stable release managed by dUhEnC-39
Learn more at: https://github.com/dUhEnC-39/secretrandom
    '''

def randchar(length: int):
    characters = list(string.ascii_letters + string.digits + string.punctuation)
    random.shuffle(characters)
    SystemRandom.shuffle(characters)
    password = ''
    [password := password + secrets.choice(characters) for _ in range(length - 1)]
    password += random.choice(characters)
    return password


def randcode(length: int):
    code = ''
    code += random.choice(shuffled_digits_for_unprdictibility)
    [
        code := code + secrets.choice(shuffled_digits_for_unprdictibility)
        for _ in range(length - 1)
    ]
    return int(code)

def product_id(segment_length: int, length: int):
    def character_gen():
        valid_characters = string.ascii_uppercase + string.digits
        character = randchar(1)
        return character if character in valid_characters else character_gen()

    def product_key_segment_gen():
        product_key_segment = ''
        [product_key_segment := product_key_segment + character_gen() for _ in range(segment_length)]
        return product_key_segment

    return '-'.join([product_key_segment_gen() for _ in range(length)])


def token_hex(length: int):
    return secrets.token_hex(length)

def token_bytes(length: int):
    return secrets.token_bytes(length)

def vigenere_cipher(message: str, key, direction=1):
    # Taken from freeCodeCamp's Scientific Computing course: Cipher lesson
    # Modified to be optimized.
    key_index = 0
    alphabet = string.ascii_lowercase
    final_message = ''
    key = key.lower()
    if not key or not all(c in alphabet for c in key):
        raise ValueError("Key must be non-empty and only contain letters a-z.")

    for char in message:
        if char.isalpha():
            is_upper = char.isupper()
            char_lower = char.lower()
            key_char = key[key_index % len(key)]
            offset = alphabet.index(key_char)
            index = alphabet.index(char_lower)
            new_index = (index + offset * direction) % len(alphabet)
            cipher_char = alphabet[new_index]
            final_message += cipher_char.upper() if is_upper else cipher_char
            key_index += 1
        else:
            final_message += char
    return final_message

def caesar_cipher(message: str, offset=3):
    alphabet = string.ascii_lowercase
    final_message = ''
    for char in message:
        if char.isalpha():
            is_upper = char.isupper()
            char_lower = char.lower()
            index = alphabet.index(char_lower)
            new_index = (index + offset) % len(alphabet)
            cipher_char = alphabet[new_index]
            final_message += cipher_char.upper() if is_upper else cipher_char
        else:
            final_message += char
    return final_message

def atbash_cipher(message: str):
    alpha = string.ascii_lowercase
    alpha_reversed = alpha[::-1]
    final_message = ''
    for char in message:
        if char.isalpha():
            is_upper = char.isupper()
            char_lower = char.lower()
            idx = alpha.index(char_lower)
            cipher_char = alpha_reversed[idx]
            final_message += cipher_char.upper() if is_upper else cipher_char
        else:
            final_message += char
    return final_message

def ascii_binary_to_text(binary_code):
    binary_values = binary_code.split(' ')
    ascii_characters = [chr(int(bv, 2)) for bv in binary_values]
    return ''.join(ascii_characters)

def text_to_ascii_binary(text):
    binary_values = [format(ord(char), '08b') for char in text]
    return ' '.join(binary_values)

# Random module features start here
def randint(from_this, to_this, step=1):
    the_repeating_number_to_loop = secrets.choice(shuffled_digits_for_unprdictibility)
    [
        SystemRandom.randrange(from_this, to_this + 1, step)
        for _ in range(random.randint(1, 22))
    ]
    return SystemRandom.randrange(from_this, to_this + 1, step)


def randflt(from_this, to_this):
    [SystemRandom.uniform(from_this, to_this) for _ in range(randint(2, 23))]
    return SystemRandom.uniform(from_this, to_this)

def choice(i):
    return secrets.choice(i)

def shuffle(i):
    if len(i) == 1:
        return i
    else:
        [SystemRandom.shuffle(i) for _ in range(randint(4, 25))]
        i[-1], i[-2] = i[-2], i[-1]
        return i
