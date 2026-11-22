import os
import random

def try_loading_words(word_bank_filepath):
    ''' Try loading words from the word bank file and return a list of words. '''

    if not os.path.exists(word_bank_filepath):
        return None

    words = []    
    print("\x1b[34mLoading words...\x1b[0m")

    with open(word_bank_filepath, "rt") as file:
        while True:
            line = file.readline()
            if len(line) <= 0:
                break

            if line.startswith("#"): # maybe a comment
                continue

            line = line.strip()
            line = line.split(None)

            words.extend(line)
    
    print(f"\x1b[32m{len(words)} words loaded successfully!\x1b[0m")

    return words

def get_words_with_letter_count(words, letter_count):
    ''' Get a list of words with the specified letter count. '''
    
    return [word for word in words if len(word) == letter_count]

def get_random_word(words):
    ''' Get a random word from the word bank. '''
    return random.choice(words)

# TODO: replace with binary search
def can_word_be_found(words, text):
    '''
    Tests if the word can be found in the word bank. Case-insensitive.
    The word list must be sorted beforehand.
    '''
    
    if text is None:
        return False

    text = text.strip().lower()
    for word in words:
        if text == word.lower():
            return True

    return False
