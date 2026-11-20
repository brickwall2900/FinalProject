from common import str_to_bool, safeint, find, list_safe_get
import persistence

def load_settings(ctx):
    ''' Loads game settings. '''
    ctx["settings"] = {
        "words_in_random": True,
        "show_words_in_advance": True,
        "letter_count_to_include": [3, 4, 5],
        "word_count_per_letter_count": { 3: 7, 4: 7, 5: 7 },
        "score_per_letter_count": { 3: 2, 4: 5, 5: 7 },
    }

    # load settings
    settings_loaded = persistence.load_persistence("typing_game")
    if settings_loaded is None:
        print("[+] New settings will be saved for this game.")
        save_settings(ctx["settings"])
    else:
        parsed_settings = __parse_settings(settings_loaded)
        if parsed_settings is not None:
            ctx["settings"] = parsed_settings
        else:
            print("[*] Settings file may be corrupt. Using defaults.")
        print("[*] Loaded settings!")

def __parse_settings(settings_loaded):
    ''' Returns a settings dict parsed from settings_loaded. ''' 
    parsed_settings = {}

    parsed_settings["words_in_random"] = str_to_bool(settings_loaded.get("words_in_random", "False"))
    parsed_settings["show_words_in_advance"] = str_to_bool(settings_loaded.get("show_words_in_advance", "False"))

    # spliti setting by , and type casts into an int
    letter_count_to_include = [safeint(letter) for letter in settings_loaded.get("letter_count_to_include", "").split(",")]
    # remove None elements
    letter_count_to_include = [x for x in letter_count_to_include if x is not None]

    parsed_settings["letter_count_to_include"] = letter_count_to_include

    word_count_per_letter_count = {}
    score_per_letter_count = {}
    for letters in letter_count_to_include:
        word_count_per_letter_count[letters] = safeint(settings_loaded.get(f"word_count_per_letter_count_{letters}"), 5)
        score_per_letter_count[letters] = safeint(settings_loaded.get(f"score_per_letter_count_{letters}"), 5)

    parsed_settings["word_count_per_letter_count"] = word_count_per_letter_count
    parsed_settings["score_per_letter_count"] = score_per_letter_count

    return parsed_settings

def save_settings(settings):
    saved_settings = {
        "words_in_random": settings["words_in_random"],
        "show_words_in_advance": settings["show_words_in_advance"],
        # yeah i know what ",".join does now lol
        "letter_count_to_include": ",".join([str(x) for x in settings["letter_count_to_include"]])
    }

    for letter_count in settings["letter_count_to_include"]:
        saved_settings[f"word_count_per_letter_count_{letter_count}"] = str(list_safe_get(settings.get("word_count_per_letter_count"), letter_count))
        saved_settings[f"score_per_letter_count_{letter_count}"] = str(list_safe_get(settings.get("score_per_letter_count"), letter_count))

    persistence.save_persistence("typing_game", saved_settings)
    print("[+] Saved settings!")

def settings(settings):
    message = ""
    while True:
        print(" *** Settings ***")
        print(" - [1]: Words shuffled randomly")
        print(" - [2]: Show words in advance")
        print(" - [3]: Letter counts")
        print()
        print(" - [0]: Exit")
        print(message)
        chosen = safeint(input("> "))
        
        if chosen is None:
            message = "Invalid option, try again."
            continue

        message = ""
        
        if chosen == 1:
            __edit_boolean_setting(settings, "words_in_random", "Words shuffled randomly", "Words are shuffled in-game. If TRUE, next words are shuffled. Otherwise, words appear in letter-count order.")
        elif chosen == 2:
            __edit_boolean_setting(settings, "show_words_in_advance", "Show words in advance", "Show next words that will be typed.")
        elif chosen == 3:
            __edit_letter_counts(settings)
        elif chosen == 0:
            break
        else:
            message = "Invalid option, try again."

def __edit_boolean_setting(settings, key, name, description):
    print("[!] ", end="")
    print(name)
    print(description)

    current_value = settings.get(key)

    print(f" - [1]: Toggle ({current_value} -> {not current_value})")
    print(" - [Any]: Leave it as it is")

    chosen = safeint(input("> "))
    if chosen is not None and chosen == 1:
        settings[key] = not settings.get(key)
        print("[+] Toggled.")
    else:
        print("[.] Left as it is.")

def __edit_letter_count_subsetting(settings, key, prompt, error_condition_message):
    letter_count = safeint(input("How many letters to change? "))
    if letter_count is None:
        return "[x] Invalid number of letters"

    if find(settings.get("letter_count_to_include", []), letter_count) is None:
        return "[x] Letter count not included"

    prop_value = safeint(input(prompt))
    if prop_value is None:
        return "[x] " + error_condition_message

    settings[key][letter_count] = prop_value
    return ""

# this function went every restriction i had
def __edit_letter_counts(settings):
    letter_count_to_include = settings.get("letter_count_to_include", [])
    message = ""
    while True:
        print("[!] Letter counts")
        print("Current included letter counts for game: ")
        for letter_count in letter_count_to_include:
            word_count = settings.get('word_count_per_letter_count', {}).get(letter_count, '0')
            score = settings.get('score_per_letter_count', {}).get(letter_count, '0')
            print(f"* {letter_count}-letter words: {word_count} words, {score} points")

        print(" - [1]: Add letter count")
        print(" - [2]: Remove letter count")
        print(" - [3]: Change word count")
        print(" - [4]: Change score")
        print()
        print(" - [0]: Back")
        print(message)

        chosen = safeint(input("> "))
        message = ""

        if chosen is None:
            continue

        if chosen == 0:
            break
        elif chosen == 1:
            letter_count = safeint(input("How many letters to add? "))
            if letter_count is None:
                message = "[x] Invalid number of letters"
                continue

            if find(letter_count_to_include, letter_count) is not None:
                message = "[x] Letter count already included"
                continue

            word_count = safeint(input("How many words should show up? "))
            if word_count is None:
                message = "[x] Invalid number of words"
                continue

            score = safeint(input("How many points is the word worth? "))
            if score is None:
                message = "[x] Invalid score number"
                continue

            letter_count_to_include.append(letter_count)
            settings["letter_count_to_include"] = letter_count_to_include
            settings["word_count_per_letter_count"][letter_count] = word_count
            settings["score_per_letter_count"][letter_count] = score
        elif chosen == 2:
            letter_count = safeint(input("How many letters to remove? "))
            if letter_count is None:
                message = "[x] Invalid number of letters"
                continue

            if find(letter_count_to_include, letter_count) is None:
                message = "[x] Letter count already not included"
                continue

            letter_count_to_include.remove(letter_count)
            settings["letter_count_to_include"] = letter_count_to_include
        elif chosen == 3:
            message = __edit_letter_count_subsetting(settings, "word_count_per_letter_count",
                                           "How many words should show up?", "Invalid number of words")
        elif chosen == 4:
            message = __edit_letter_count_subsetting(settings, "score_per_letter_count",
                                            "How many points is the word worth?", "Invalid score number")
        else:
            print("Invalid option, try again.")
