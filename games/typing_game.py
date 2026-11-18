import time
import random

from common import print_error, str_to_bool, safeint, sort, find, pause, clamp, get_whole_digits
import data.word_bank as word_bank_helper
import persistence

def call(g_ctx):
    # small boilerplate
    if init(g_ctx):
        run(g_ctx)

    destroy(g_ctx)

def init(g_ctx):
    # create empty context for game
    g_ctx["typing_game"] = {}
    
    __load_settings(g_ctx["typing_game"])

    return True

def __load_settings(ctx):
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
        __save_settings(ctx["settings"])
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
    letter_count_to_include = [safeint(letter) for letter in settings_loaded.get("show_words_in_advance", "").split(",")]
    # remove None elements
    letter_count_to_include = [x for x in letter_count_to_include if x is not None]

    parsed_settings["letter_count_to_include"] = letter_count_to_include

    # if the list if empty, stop cuz we can't have 0 letters
    if len(letter_count_to_include) == 0:
        return None

    word_count_per_letter_count = {}
    score_per_letter_count = {}
    for letters in letter_count_to_include:
        word_count_per_letter_count[letters] = safeint(settings_loaded.get(f"word_count_per_letter_count_{letters}"), 5)
        score_per_letter_count[letters] = safeint(settings_loaded.get(f"score_per_letter_count_{letters}"), 5)

    return parsed_settings

def __save_settings(settings):
    saved_settings = {
        "words_in_random": settings["words_in_random"],
        "show_words_in_advance": settings["show_words_in_advance"],
        # yeah i know what ",".join does now lol
        "letter_count_to_include": ",".join([str(x) for x in settings["letter_count_to_include"]])
    }

    for letter_count in settings["letter_count_to_include"]:
        saved_settings[f"word_count_per_letter_count_{letter_count}"] = str(settings["word_count_per_letter_count"][letter_count])
        saved_settings[f"score_per_letter_count_{letter_count}"] = str(settings["score_per_letter_count"][letter_count])

    persistence.save_persistence("typing_game", saved_settings)
    print("[+] Saved settings!")

def run(g_ctx):
    typing_game_ctx = g_ctx["typing_game"]
    words = g_ctx["words"]

    while True:
        print(" ~~~ The Typing Game ~~~")
        print("The Typing Game tests your typing skills by you typing words with speed and accuracy!")
        print(" - [1]: Start")
        print(" - [2]: Leaderboards")
        print(" - [3]: Settings")
        print(" - [4]: About")
        print()
        print(" - [0]: Exit")
        chosen = safeint(input("> "))
        
        if chosen is None:
            print("Invalid option, try again.")
            continue
        
        if chosen == 1:
            game(typing_game_ctx, words)
        elif chosen == 2:
            __view_leaderboard()
        elif chosen == 3:
            __settings(typing_game_ctx["settings"])
            __save_settings(typing_game_ctx["settings"])
        elif chosen == 4:
            __view_about()
        elif chosen == 0:
            break
        else:
            print("Invalid option, try again.")
    
def __settings(settings):
    while True:
        print(" *** Settings ***")
        print(" - [1]: Words shuffled randomly")
        print(" - [2]: Show words in advance")
        print(" - [3]: Letter counts")
        print()
        print(" - [0]: Exit")
        chosen = safeint(input("> "))
        
        if chosen is None:
            print("Invalid option, try again.")
            continue
        
        if chosen == 1:
            __edit_boolean_setting(settings, "words_in_random", "Words shuffled randomly", "Words are shuffled in-game. If TRUE, next words are shuffled. Otherwise, words appear in letter-count order.")
        elif chosen == 2:
            __edit_boolean_setting(settings, "show_words_in_advance", "Show words in advance", "Show next words that will be typed.")
        elif chosen == 3:
            __edit_letter_counts(settings)
        elif chosen == 0:
            break
        else:
            print("Invalid option, try again.")

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

# this function went every restriction i had
def __edit_letter_counts(settings):
    letter_count_to_include = settings.get("letter_count_to_include", [])
    while True:
        print("[!] Letter counts")
        print("Current included letter counts for game: ")
        for letter_count in letter_count_to_include:
            word_count = settings.get('word_count_per_letter_count', {}).get(letter_count, '0')
            score = settings.get('score_per_letter_count', {}).get(letter_count, '0')
            print(f"* {letter_count}-letter words: {word_count} words, {score} points")

        print(f" - [1]: Add letter count")
        print(f" - [2]: Remove letter count")
        print(f" - [3]: Change word count")
        print(f" - [4]: Change score")
        print()
        print(" - [0]: Back")

        chosen = safeint(input("> "))
        if chosen is None:
            continue

        if chosen == 0:
            break
        elif chosen == 1:
            letter_count = safeint(input("How many letters to add? "))
            if letter_count is None:
                print("[x] Invalid number of letters")
                continue

            if find(letter_count_to_include, letter_count) is not None:
                print("[x] Letter count already included")
                continue

            word_count = safeint(input("How many words should show up? "))
            if word_count is None:
                print("[x] Invalid number of words")
                continue

            score = safeint(input("How many points is the word worth? "))
            if score is None:
                print("[x] Invalid score number")
                continue

            letter_count_to_include.append(letter_count)
            settings["letter_count_to_include"] = letter_count_to_include
            settings["word_count_per_letter_count"][letter_count] = word_count
            settings["score_per_letter_count"][letter_count] = score
        elif chosen == 2:
            letter_count = safeint(input("How many letters to remove? "))
            if letter_count is None:
                print("[x] Invalid number of letters")
                continue

            if find(letter_count_to_include, letter_count) is None:
                print("[x] Letter count already not included")
                continue

            letter_count_to_include.remove(letter_count)
            settings["letter_count_to_include"] = letter_count_to_include
        elif chosen == 3:
            letter_count = safeint(input("How many letters to change word count? "))
            if letter_count is None:
                print("[x] Invalid number of letters")
                continue

            if find(letter_count_to_include, letter_count) is None:
                print("[x] Letter count not included")
                continue

            word_count = safeint(input("How many words should show up? "))
            if word_count is None:
                print("[x] Invalid number of words")
                continue

            settings["word_count_per_letter_count"][letter_count] = word_count
        elif chosen == 4:
            letter_count = safeint(input("How many letters to change score? "))
            if letter_count is None:
                print("[x] Invalid number of letters")
                continue

            if find(letter_count_to_include, letter_count) is None:
                print("[x] Letter count not included")
                continue

            score = safeint(input("How many points is the word worth? "))
            if score is None:
                print("[x] Invalid score number")
                continue

            settings["score_per_letter_count"][letter_count] = score
        else:
            print("Invalid option, try again.")

def __view_about():
    print("The Typing Game tests how fast you can type words correctly!!" \
    " Type more words correctly, the more points you get. Better if you can type" \
    " words with speed and accuracy!")
    pause()

    print("TLDR; Type correct words = more points")
    print("The below example will mark your input as CORRECT")
    print()
    print("test")
    print()
    print("> test (<- this is your input box)")
    
    pause()

    print("The below example will mark your input as INCORRECT; you get 0 points.")
    print()
    print("hello")
    print()
    print("> henlo")

    pause()

def game(ctx, word_bank):
    settings = ctx["settings"]
    success = __validate_invariants(settings)

    if not success:
        print("One or more settings are invalid.")
        return

    words = __build_word_sequence(settings, word_bank)

    if words is None:
        print("The game cannot be started.")
        return

    __print_countdown()

    timestamp_start = time.time()
    user_typed_words = []
    for i in range(len(words)):
        word = words[i]
        __print_word(word, words[i+1:], settings)

        user_input = input()
        user_typed_words.append(user_input)

    time_taken = time.time() - timestamp_start
    success, score, judgement_table = __judge(words, user_typed_words, settings)
    if success:
        __print_congrats(time_taken, score, judgement_table)
    else:
        print(f"The score could not be calculated.")

# picks random words with a criteria, that `count`
# words will be given with `letter_count` letters in it from the word bank.
def __pick_words(word_count, letter_count, word_bank):
    letter_count_words = word_bank_helper.get_words_with_letter_count(word_bank, letter_count)

    if len(letter_count_words) < word_count:
        return None

    random.seed()
    random.shuffle(letter_count_words)

    return letter_count_words[:word_count]

def __build_word_sequence(settings, word_bank):
    result = []

    for letter_count in settings["letter_count_to_include"]:
        word_count = settings["word_count_per_letter_count"][letter_count]
        words = __pick_words(word_count, letter_count, word_bank)
        if words is not None:
            result.extend(words)
        else:
            print_error(f"Insufficient words in word bank. Please provide more {letter_count}-letter words.")
            return None

    if settings["words_in_random"]:
        random.seed()
        random.shuffle(result)

    return result

def __validate_invariants(settings):
    '''
    Checks the settings if all setting is valid.
    Returns True if all settings are valid, False otherwise.
    '''
    if len(settings["letter_count_to_include"]) <= 0:
        print_error("At least one n-letter count must be specified.")
        return False

    for letter_count in settings["letter_count_to_include"]:
        if not letter_count in settings["word_count_per_letter_count"]:
            print_error(f"The word count for {letter_count}-letter words is unspecified.")
            return False

        if not letter_count in settings["score_per_letter_count"]:
            print_error(f"The score for {letter_count}-letter words is unspecified.")
            return False

    return True

def __judge(correct_input_list, user_input_list, settings):
    if len(correct_input_list) < len(user_input_list):
        print_error("You did not type enough words to be judged. How?")
        return False, 0, []

    # list of tuples (correct_word, user_input_word, score)
    judgement_table = []
    total_score = 0

    for i in range(len(correct_input_list)):
        correct_input = correct_input_list[i]
        user_input = user_input_list[i]

        letter_count = len(correct_input)

        if not letter_count in settings["score_per_letter_count"]:
            print_error(f"Score per {letter_count}-letter word is missing right now... How come?")
            return False, 0, []

        given_score = settings["score_per_letter_count"][letter_count]
        is_correct = correct_input == user_input
        if is_correct:
            total_score += given_score

        judgement_table.append((correct_input, user_input, (given_score if is_correct else 0)))

    return True, total_score, judgement_table

def __print_countdown():
    countdown = ""

    print("The typing game starts in...")

    for i in range(4, 0, -1):
        if i == 1:
            countdown += "GOO!!!!"
        elif (i - 1) < 4:
            countdown += f"{i - 1}... "

        print(countdown)
        time.sleep(0.5)

def __print_word(word, future_words, settings):
    # get the 5 first future words
    future_words_printed = " ".join([future_words[i] for i in range(len(future_words)) if i < 5]) if settings["show_words_in_advance"] else ""

    print("TYPE THE HIGHLIGHTED WORD BELOW THEN PRESS [Enter]")
    print(f">> {word} << {future_words_printed}")
    print("> ", end="")

def __print_congrats(time_taken, score, judgement_table):
    submitted = False
    while True:
        print("~~~^ CONGRATULATIONS ^~~~")
        print(f"Congratulations! You took {time_taken:.2f} seconds to type all words.")
        print()
        print(f"Your score is {score}. Good job!")

        print(" - [1] View Score Table")
        print(" - [2] Submit to Leaderboard")
        print(" - [0] Exit")

        chosen = safeint(input("> "))
        if chosen is None:
            print("Invalid option, try again.")
            continue

        if chosen == 1:
            __view_score_table(judgement_table)
        elif chosen == 2 and not submitted:
            __save_to_leaderboard(time_taken, score, judgement_table)
            submitted = True
        elif chosen == 0:
            break
        else:
            print("Invalid option, try again.")

def __save_to_leaderboard(time_taken, score, judgement_table):
    name = input("What is your name? ")
    # hmmm
    # FIXME: my prefrontal cortex is shut down
    # fuck

    leaderboard = persistence.load_persistence("leaderboard-typing_game")
    current_entry = 0

    if leaderboard is not None:
        current_entry = safeint(leaderboard.get("CurrentEntry"), 0)
        current_entry += 1

        leaderboard["CurrentEntry"] = str(current_entry)
    else:
        leaderboard = {}
        leaderboard["CurrentEntry"] = "0"
    
    leaderboard[f"Entry{current_entry}"] = name
    leaderboard[f"Entry{current_entry}_time_taken"] = str(int(time_taken * 100))
    leaderboard[f"Entry{current_entry}_score"] = str(score)
    leaderboard[f"Entry{current_entry}_judgement_count"] = str(len(judgement_table))

    for index in range(len(judgement_table)):
        entry = judgement_table[index]
        leaderboard[f"Entry{current_entry}_judgement_{index}_correct"] = entry[0]
        leaderboard[f"Entry{current_entry}_judgement_{index}_user"] = entry[1]
        leaderboard[f"Entry{current_entry}_judgement_{index}_score"] = str(entry[2])

    persistence.save_persistence("leaderboard-typing_game", leaderboard)

    __view_leaderboard()

def __leaderboard_comparator(this, that):
    this_score = this[2]
    that_score = that[2]
    if this_score != that_score:
        return (that_score - this_score)
    else: # if same score, compare by time instead.
        this_time = this[1]
        that_time = that[1]
        return (that_time - this_time)

def __parse_leaderboard(loaded_leaderboard):
    the_leaderboard = []

    entry_count = safeint(loaded_leaderboard.get("CurrentEntry"), 0)

    for i in range(entry_count + 1):
        entry_key = f"Entry{i}"

        name = loaded_leaderboard.get(entry_key)
        if name is None:
            continue

        time = safeint(loaded_leaderboard.get(entry_key + "_time_taken"))
        score = safeint(loaded_leaderboard.get(entry_key + "_score"))
        judgement_table_count = safeint(loaded_leaderboard.get(entry_key + "_judgement_count"))

        if time is None or score is None or judgement_table_count is None:
            continue

        time = time / 100 # compensate float to int by division by 100

        missing = False
        judgement_table = []
        for judgement_table_index in range(judgement_table_count):
            judgement_entry_key = entry_key + f"_judgement_{judgement_table_index}"
            correct_word = loaded_leaderboard.get(judgement_entry_key + "_correct")
            user_typed_word = loaded_leaderboard.get(judgement_entry_key + "_user")
            word_score = safeint(loaded_leaderboard.get(judgement_entry_key + "_score"))

            if correct_word is None or user_typed_word is None or word_score is None:
                missing = True
                break
            judgement_table.append((correct_word, user_typed_word, word_score))

        if missing:
            continue

        the_leaderboard.append((name, time, score, judgement_table))

    return the_leaderboard

def __paginate_and_navigate_leaderboard(leaderboard):
    page_offset = 0
    page_count = len(leaderboard)
    max_page_view = 10

    while True:
        print(" ^^^ Leaderboard ^^^")

        for index in range(page_offset, min(page_count, page_offset + max_page_view)):
            entry = leaderboard[index]
            name = entry[0]
            time = entry[1]
            score = entry[2]

            print(f" - [{(index - page_offset) + 1}]: {name}; {time} seconds; {score} pts.")

        show_next = page_offset < page_count - max_page_view
        show_prev = 0 < page_offset - max_page_view

        print()
        if show_prev:
            print(" - [Q]: Previous")
        if show_next:
            print(" - [W]: Next")
        print(" - [0]: Exit")
        raw_chosen = input("> ").lower().strip()
        chosen = safeint(raw_chosen)

        if chosen is None:
            if raw_chosen.startswith("q") and page_offset - max_page_view >= 0:
                page_offset = page_offset - max_page_view
            elif raw_chosen.startswith("w") and page_offset + max_page_view < page_count - 1:
                page_offset = page_offset + max_page_view
            else:
                print("Invalid option, try again.")
            continue

        if chosen == 0:
            break
        else:
            real_index = (chosen + page_offset) - 1 
            if not (0 <= real_index < page_count):
                print("Invalid option, try again.")
                continue
            leaderboard_entry = leaderboard[real_index]
            __view_score_table(leaderboard_entry[3], leaderboard_entry[0])

def __view_leaderboard():
    loaded_leaderboard = persistence.load_persistence("leaderboard-typing_game")

    if loaded_leaderboard is None:
        print_error("Leaderboard cannot be loaded because you haven't played a game yet, or because of file corruption.")
        return

    the_leaderboard = __parse_leaderboard(loaded_leaderboard)

    sort(the_leaderboard, __leaderboard_comparator)

    __paginate_and_navigate_leaderboard(the_leaderboard)

def __view_score_table(judgement_table, name=None):
    # (correct_word, user_input_word, score)
    page_offset = 0
    page_count = len(judgement_table)
    max_page_view = 10

    while True:
        print(f" ^^^ Viewing scores{ (' for ' + name) if name is not None else ''} ^^^")
        
        longest_correct_word = 0
        longest_user_word = 0
        for entry in judgement_table:
            longest_correct_word = len(entry[0]) if len(entry[0]) > longest_correct_word else longest_correct_word
            longest_user_word = len(entry[1]) if len(entry[1]) > longest_user_word else longest_user_word
        longest_correct_word += 1
        longest_user_word += 1

        for index in range(page_offset, min(page_count, page_offset + max_page_view)):
            entry = judgement_table[index]
            visual_index = index - page_offset + 1
            correct_word = entry[0] # type: str
            user_input_word = entry[1] # type: str
            score = entry[2]
            
            correct_word = correct_word.ljust(max(longest_correct_word - get_whole_digits(visual_index) + 1, 0))
            user_input_word = user_input_word.ljust(max(longest_user_word, 0))

            print(f" - [{visual_index}]: {correct_word} | {user_input_word}| +{score} pts.")

        print()
        print(" - [Q]: Previous")
        print(" - [W]: Next")
        print(" - [0]: Exit")
        raw_chosen = input("> ").lower().strip()
        chosen = safeint(raw_chosen)

        if chosen is None:
            if raw_chosen.startswith("q") and page_offset - max_page_view >= 0:
                page_offset = page_offset - max_page_view
            elif raw_chosen.startswith("w") and page_offset + max_page_view < page_count - 1:
                page_offset = page_offset + max_page_view
            else:
                print("Invalid option, try again.")
            continue

        if chosen == 0:
            break


def destroy(ctx):
    # destroy typing game context
    del ctx["typing_game"]

# def __settings():
    # pass
    # def boolean_setting(key, name, description):
    #     def proc():
            
    #         procedures_list = [
    #             procedures.defproc(1, "Toggle", None),
    #             procedures.defproc(0, "Go Back", None)
    #         ]

    #         description_display = f"{description}\n \nCurrent value: {str(__get_setting(key)).upper()}"

    #         while True:
    #             status_code, option, _ = procedures.ask_procedure(name, "?",
    #                                                     procedures_list,
    #                                                     after_header=description_display)
    #             if status_code == STATUS_SUCCESS:
    #                 if option == 0:
    #                     break
    #                 elif option == 1:
    #                     settings[key] = not __get_setting(key)

    #             description_display = f"{description}\n \nCurrent value: {str(__get_setting(key)).upper()}"

    #     return proc

    # def __opt_letter_counts():
    #     procedures_list = [
    #         procedures.defproc(1, "Add", None),
    #         procedures.defproc(2, "Remove", None),
    #         procedures.defproc(0, "Go Back", None)
    #     ]

    #     description = f"Letter counts.\n \nCurrent value: {str(__get_setting("letter_count_to_include")).upper()}"

    #     while True:
    #         status_code, option, _ = procedures.ask_procedure("Letter counts", "?",
    #                                                 procedures_list,
    #                                                 after_header=description)
    #         if status_code == STATUS_SUCCESS:
    #             if option == 0:
    #                 break
    #             elif option == 1:
    #                 count = dialog.input("How many letters?", "Letter counts")
    #                 count = safeint(count)
    #                 if count is not None and find(__get_setting("letter_count_to_include"), count) is None:
    #                     __get_setting("letter_count_to_include").append(count)
    #                 else:
    #                     print_error("Letter count is invalid or already included.")
    #             elif option == 2:
    #                 count = dialog.input(f"Specify letter count to remove? ({__get_setting("letter_count_to_include")})", "Letter counts")
    #                 count = safeint(count)
    #                 if count is not None and find(__get_setting("letter_count_to_include"), count) is not None:
    #                     __get_setting("letter_count_to_include").remove(count)
    #                 else:
    #                     print_error("Letter count is invalid or not in the list.")

    #         description = f"Letter counts.\n \nCurrent value: {str(__get_setting("letter_count_to_include")).upper()}"

    # def letter_setting(key, title, description):
    #     def proc():
    #         def __edit_for_letter_count(letter_count):
    #             def proc():
    #                 new_value = dialog.input(f"{description} (for {letter_count}-letter words).\n \nCurrent: {__get_setting(key)[letter_count]}")
    #                 new_value = safeint(new_value)
    #                 if new_value:
    #                     __get_setting(key)[letter_count] = new_value
    #                 else:
    #                     print_error("Bad value specified.")
    #             return proc

    #         procedures_list = [
    #             procedures.defproc(0, "Go Back", None)
    #         ]

    #         item = 1
    #         for k in __get_setting(key).keys():
    #             procedures_list.append(procedures.defproc(item, f"{k}-letter words", __edit_for_letter_count(k)))
    #             item += 1

    #         status_footer = None
    #         while True:
    #             status_code, option, _ = procedures.ask_procedure(title, "?",
    #                                                     procedures_list,
    #                                                     after_header="Choose the letter count",
    #                                                     status_footer=status_footer)

    #             if status_code != STATUS_SUCCESS:
    #                 status_footer = "Invalid option."
    #                 continue
    #             else:
    #                 status_footer = None
    
    #             if option == 0:  # exit option
    #                 break

    #             procedures.do_execute_procedure(procedures_list, option)
    #     return proc

    # procedures_list = [
    #     procedures.defproc(1, "Words shuffled randomly", boolean_setting("words_in_random", "Words shuffled randomly", "Words are shuffled in-game. If TRUE, next words are shuffled. Otherwise, words appear in letter-count order.")),
    #     procedures.defproc(2, "Show words in advance", boolean_setting("show_words_in_advance", "Show words in advance", "Show next words that will be typed.")),
    #     procedures.defproc(3, "Letter counts", __opt_letter_counts),
    #     procedures.defproc(4, "Word counts", letter_setting("word_count_per_letter_count", "Word counts", "Choose the number of times these number of words appear in a game.")),
    #     procedures.defproc(5, "Score per letter count", letter_setting("score_per_letter_count", "Score per letter count", "Choose how much score given for these number of words if typed correctly")),
    #     procedures.defproc(0, "Exit", None)
    # ]

    # status_footer = None
    # procedure_offset = 0
    # while True:
    #     status_code, option, _ = procedures.ask_procedure("Settings", "?",
    #                                                                     procedures_list,
    #                                                                     status_footer=status_footer,
    #                                                                     after_header=RULES,
    #                                                                     procedure_offset=procedure_offset)

    #     if status_code == STATUS_NEXT and option is not None:
    #         procedure_offset += option
    #         continue
    #     elif status_code == STATUS_PREVIOUS and option is not None:
    #         procedure_offset -= option
    #         continue
        
    #     status_code = procedures.do_execute_procedure(procedures_list, option)
    #     if status_code != STATUS_SUCCESS:
    #         status_footer = "Invalid option."
    #         continue
    #     else:
    #         status_footer = None

    #     if option == 0:  # exit option
    #         __save_settings()
    #         break