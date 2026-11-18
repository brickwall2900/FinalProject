import time
import random

from common import print_error, safeint
import data.word_bank as word_bank_helper

from games.typing_game.settings import load_settings, settings, save_settings
from games.typing_game.leaderboards import view_leaderboard
from games.typing_game.ui import view_about, print_congrats, print_countdown, print_word

def call(g_ctx):
    # small boilerplate
    if init(g_ctx):
        run(g_ctx)

    destroy(g_ctx)

def init(g_ctx):
    # create empty context for game
    g_ctx["typing_game"] = {}
    
    load_settings(g_ctx["typing_game"])

    return True

def run(g_ctx):
    typing_game_ctx = g_ctx["typing_game"]
    words = g_ctx["words"]

    message = ""
    while True:
        print(" ~~~ The Typing Game ~~~")
        print("The Typing Game tests your typing skills by you typing words with speed and accuracy!")
        print(" - [1]: Start")
        print(" - [2]: Leaderboards")
        print(" - [3]: Settings")
        print(" - [4]: About")
        print()
        print(" - [0]: Exit")
        print(message)
        chosen = safeint(input("> "))

        message = ""
        
        if chosen is None:
            message = "Invalid option, try again."
            continue
        
        if chosen == 1:
            game(typing_game_ctx, words)
        elif chosen == 2:
            view_leaderboard()
        elif chosen == 3:
            settings(typing_game_ctx["settings"])
            save_settings(typing_game_ctx["settings"])
        elif chosen == 4:
            view_about()
        elif chosen == 0:
            break
        else:
            message = "Invalid option, try again."

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

    print_countdown()

    timestamp_start = time.time()
    user_typed_words = []
    for i in range(len(words)):
        word = words[i]
        print_word(word, words[i+1:], settings)

        user_input = input()
        user_typed_words.append(user_input)

    time_taken = time.time() - timestamp_start
    success, score, judgement_table = __judge(words, user_typed_words, settings)
    if success:
        print_congrats(time_taken, score, judgement_table)
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
    if len(correct_input_list) != len(user_input_list):
        print_error("You did not type enough words or too much words to be judged. How?")
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


def destroy(ctx):
    # destroy typing game context
    del ctx["typing_game"]
