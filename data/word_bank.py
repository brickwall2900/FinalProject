import os
import common

from status import STATUS_ALREADY_EXISTS, STATUS_FILE_NOT_FOUND, STATUS_SUCCESS

WORD_BANK_FILEPATH_DEFAULT = os.path.join("data", "english3.txt")

words = []
loaded = False
loaded_filepath = WORD_BANK_FILEPATH_DEFAULT

# Try loading words if it has already been loaded.
# Skip loading if it has been loaded.
def try_loading_words(word_bank_filepath = WORD_BANK_FILEPATH_DEFAULT):
    global loaded

    if loaded:
        return STATUS_ALREADY_EXISTS, None

    if not os.path.exists(word_bank_filepath):
        return STATUS_FILE_NOT_FOUND, None

    word_count = 0
    print("Loading words...")

    with open(word_bank_filepath, "rt", 1) as file:
        while True:
            line = file.readline()
            if len(line) <= 0:
                break

            if line.startswith("#"):
                continue

            line = line.strip()
            line = line.split(None)

            word_count += len(line)
            words.extend(line)

    print(f"{word_count} words loaded successfully!")
    loaded = True

    return STATUS_SUCCESS, word_count

# Get a list of words with the specified letter count.
def get_words_with_letter_count(letter_count):
    return [word for word in words if len(word) == letter_count]

# Get a random word from the word bank
def get_random_word():
    return common.pick_randomly(words)

# Tests if the word can be found in the word bank. Case-insensitive.
# TODO: sort wordbank an d replace with binary search
def can_word_be_found(text):
    if text is None:
        return False

    text = text.strip().lower()
    for word in words:
        if text == word.lower():
            return True

    return False