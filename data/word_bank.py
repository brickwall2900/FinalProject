import os

words = []
loaded = False

WORD_BANK_FILENAME = os.path.join("data", "words_alpha.txt")
BUFFER_SIZE = 4096 * 4

ERROR_SUCCESS           = 0
ERROR_FILE_NOT_FOUND    = 1
ERROR_LOADED            = 2

# Try loading words if it has already been loaded.
# Skip loading if it has been loaded.
def try_loading_words():
    global loaded

    if loaded:
        return ERROR_LOADED, None

    if not os.path.exists(WORD_BANK_FILENAME):
        return ERROR_FILE_NOT_FOUND, None

    word_count = 0
    print("Loading words...")

    with open(WORD_BANK_FILENAME, "rt", 1) as file:
        while True:
            line = file.readline()
            if len(line) <= 0:
                break

            if line.startswith("#"):
                continue

            word_count += 1
            words.append(line)

    print(f"{word_count} words loaded successfully!")
    loaded = True

    return ERROR_SUCCESS, word_count