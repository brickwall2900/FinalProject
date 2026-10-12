import os

from status import STATUS_ALREADY_EXISTS, STATUS_FILE_NOT_FOUND, STATUS_SUCCESS

BUFFER_SIZE = 4096 * 4
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