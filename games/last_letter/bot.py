from data import word_bank

import time
import random

from common import *

def __bot_turn(words, start_or_end, letters, bot_difficulty, player_data):
    LETTER_START        = 0
    LETTER_END          = 1
    
    # bot difficulty
    # n - secs max / sluggishness secs
    # 0 - 12 / .7
    # 1 - 2 / .1
    seconds_budget = lerp(12, 2, bot_difficulty) + random.random() * 2 * (-1 if randbool() else 1)
    sluggish = lerp(.7, .1, bot_difficulty)

    time_start_timestamp = time.time()
    chosen_word = None
    correct_word = None

    # ok solve
    while True:
        if (time.time() - time_start_timestamp) > seconds_budget:
            return None

        word = word_bank.get_random_word(words)
        if start_or_end == LETTER_START:
            if str.startswith(word, letters):
                chosen_word = word
                correct_word = word
                break
        else:
            if str.endswith(word, letters):
                chosen_word = word
                correct_word = word
                break

        time.sleep(clamp(random.random() * sluggish, 0, seconds_budget - (time.time() - time_start_timestamp)))

    player_data["bot_correct_word"] = correct_word
    # how the fuck can i artifically mess upthe bot

    return chosen_word