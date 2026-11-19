import persistence

from data import word_bank

import time
import random

from common import *

# inspired by that one ropblox game i played
LETTER_START        = 0
LETTER_END          = 1

def call(g_ctx):
    if init(g_ctx):
        run(g_ctx)

    destroy(g_ctx)

def init(g_ctx):
    g_ctx["word_bomb"] = {}

    return True

def run(g_ctx):
    last_letter_ctx = g_ctx["word_bomb"]
    words = g_ctx["words"]

    message = ""
    while True:
        print(" ~~~ Word Bomb ~~~")
        print("Word Bomb is a multiplayer game. Come up with words that have the first or last letter! Last one standing alive wins.")
        print(" - [1]: PLAY!!!")
        print(" - [2]: About")
        print()
        print(" - [0]: Exit")
        print(message)
        chosen = safeint(input("> "))

        message = ""
        
        if chosen is None:
            message = "Invalid option, try again."
            continue
        
        if chosen == 1:
            game(last_letter_ctx, words)
        elif chosen == 2:
            __about()
        elif chosen == 0:
            break
        else:
            message = "Invalid option, try again."

def __about():
    print("Hi")

def __setup_player(id):
    BOT_NAMES = ["Computer", "Robot", "Bot", "AI", "CPU", "Agent", "Claude 0.1 ", "ChatGPT 1 ", "Pythonista"]
    player_data = {}

    player_name_or_bot = input("What is your name? Leave empty for bot. NAME: ")
    if player_name_or_bot is None or len(player_name_or_bot) == 0:
        random.seed()
        player_data["name"] = random.choice(BOT_NAMES) + str(id)
        player_data["real"] = False
        player_data["bot_skill"] = random.random()
    else:
        player_data["name"] = player_name_or_bot
        player_data["real"] = True

    player_data["score"] = 0
    player_data["lives"] = 3
    return player_data

def __count(players, is_a_bot):
    number = 0
    for player in players:
        if (is_a_bot and not player["real"]) or (not is_a_bot and player["real"]):
            number += 1
    return number

def game(ctx, words):
    players = [] # a list of dicts (player data)

    number_of_players = None
    while number_of_players is None:
        number_of_players_raw = input("Give the number of players that will be playing: ")
        number_of_players = safeint(number_of_players_raw)
        if number_of_players is not None and number_of_players < 2:
            print_error("Cannot have less than two players.")
            number_of_players = None # whoops
        else:
            print_error("Invalid player count.")

    for id in range(number_of_players):
        players.append(__setup_player(id))

    print("You can either have two or more keyboards connected to the same computer albeit with sabotage...\n \nOR\n \n" \
    "share one keyboard... albeit with contention.")
    pause()

    print(f"Players: {__count(players, False)} / Bots: {__count(players, True)}\n \nAre ya'll ready?")
    pause()

    __core_game_loop(players, words)

def __core_game_loop(players, words):
    previous_word = None
    time_seconds = 10
    prev_player_finish_time = None
    words_used = []
    message = None
    ranking = len(players)

    while ranking > 1:
        for player in players:
            if ranking <= 1:
                break

            if player["lives"] <= 0:
                continue

            # pick a letter first
            start_or_end, letters = __pick_letter(words, previous_word)

            name = player["name"]
            is_a_bot = not player["real"]

            judge_timestamp = time.time()
            yay = False
            while True: # turn would not end until player gets a correct word
                if player["lives"] <= 0:
                    break

                __print_letter(start_or_end, letters, name, is_a_bot, player["lives"], 10 - (time.time() - judge_timestamp), message)

                word = None
                if is_a_bot:
                    time.sleep(1)
                    word = __bot_turn(words, start_or_end, letters, player["bot_skill"], player)
                else:
                    word = __player_turn(start_or_end, letters)

                time_taken = (time.time() - judge_timestamp)
                if time_taken > time_seconds: # timed out
                    message = f"{name} timed out!"
                    break

                # judge time
                okay1 = word is not None and find(words_used, word) is None
                okay2 = word is not None and word_bank.can_word_be_found(words, word)
                okay3 = word is not None and (str.startswith(word, letters) if start_or_end == LETTER_START else str.endswith(word, letters))
                if okay1 and okay2 and okay3 and word is not None:
                    player["score"] += len(word) * 50
                    yay = True
                    prev_player_finish_time = time_taken
                    words_used.append(word)
                    message = f"{name} took {prev_player_finish_time:.2f} seconds to finish!"
                    break
                elif word is not None:
                    player["lives"] -= 1
                    if not okay1:
                        message = "You used an already submitted word! \"" + word + "\""
                    elif not okay2 or not okay3:
                        message = "You submitted an input that is not a word found in the word bank."

            if not yay: # nay
                player["lives"] -= 1

            if player["lives"] <= 0:
                message = f"Uh-oh! {name} ran out of lives and lost..."
                player["ranking"] = ranking
                ranking -= 1

    # last one standing wins rank 1
    for player in players:
        if "ranking" not in player:
            player["ranking"] = 1

    __show_leaderboard(players)

def __leaderboard_comparator(this, that):
    return this["ranking"] - that["ranking"]

def __show_leaderboard(players):
    sort(players, __leaderboard_comparator)

    page_offset = 0
    page_count = len(players)
    max_page_view = 10
    message = ""

    while True:
        print(" ^^^ Leaderboard ^^^")

        page_end = min(page_count, page_offset + max_page_view)
        items_on_page = page_end - page_offset

        for index in range(page_offset, page_end):
            player = players[index]
            name = player.get("name", "Anonymous")
            score = player.get("score", 0)

            print(f" - [{(index - page_offset) + 1}]: {name}; {score} pts.")

        show_prev = page_offset > 0
        show_next = page_end < page_count

        print()
        if show_prev:
            print(" - [Q]: Previous")
        if show_next:
            print(" - [W]: Next")
        print(" - [0]: Exit")
        print(message)
        raw_chosen = input("> ").lower().strip()
        chosen = safeint(raw_chosen)
        message = ""

        if chosen is None:
            if raw_chosen.startswith("q") and show_prev:
                page_offset = page_offset - max_page_view
            elif raw_chosen.startswith("w") and show_next:
                page_offset = page_offset + max_page_view
            else:
                message = "Invalid option, try again."
            continue

        if chosen == 0:
            break

# returns tuple (LETTER_START | LETTER_END, <chars>)
def __pick_letter(words, previous_word):
    start_or_end = LETTER_START if randbool() else LETTER_END

    # then chars
    # it needs to be something from the dictionary
    # that means we will try solving it first
    if previous_word is None:
        previous_word = word_bank.get_random_word(words)

    assert previous_word is not None

    # then try slicing it, max of 4 chars, min of 1 char
    max_chars = [x for x in range(1, 5, 1)]
    chars_to_slice_list = max_chars.copy()
    candidate_letters_percentage = {}
    random.shuffle(chars_to_slice_list) # fix this algorith TODO FIXME
    
    for word in words:
        for chars_to_slice in chars_to_slice_list:
            chosen_letters = None
            if len(previous_word) >= chars_to_slice:
                if start_or_end == LETTER_START:
                    chosen_letters = previous_word[:chars_to_slice]
                else:
                    chosen_letters = previous_word[-chars_to_slice:]
            else:
                chosen_letters = previous_word

            # we have chosen our candidate word
            # now we check if we can like choose the majority of the words in it
            # we want to make the game easy and fun
            # so what we do is compare what we chose against the word bank and calc
            # how many % the words start/end with teh candidate letter

            # fucking linear search with possible 1+ mil elements
            total_word_count = len(words)
            accepted_word_count = 0
        
            if start_or_end == LETTER_START:
                if str.startswith(word, chosen_letters):
                    accepted_word_count += 1
            else:
                if str.endswith(word, chosen_letters):
                    accepted_word_count += 1

            percentage = accepted_word_count / total_word_count
            candidate_letters_percentage[chars_to_slice] = percentage

    # then what do we do?
    # what if...

    # home of the mosdt inefficient algorithms out there
    sorted_easiest_to_hardest = []
    while len(sorted_easiest_to_hardest) < len(chars_to_slice_list):
        max = None
        max_i = None
        for i in range(len(chars_to_slice_list)):
            letter = chars_to_slice_list[i]
            if find(sorted_easiest_to_hardest, letter) is not None:
                continue

            percentage = candidate_letters_percentage[letter]
            if max is None or max < percentage:
                max_i = i
                max = percentage

        sorted_easiest_to_hardest.append(max_i)

    chosen_letter_count_idx = random.choices(sorted_easiest_to_hardest, weights=max_chars, k=1)
    chosen_letter_count = chars_to_slice_list[chosen_letter_count_idx[0]]
    # ouch...
    chosen_letters = None
    if len(previous_word) >= chosen_letter_count:
        if start_or_end == LETTER_START:
            chosen_letters = previous_word[:chosen_letter_count]
        else:
            chosen_letters = previous_word[-chosen_letter_count:]
    else:
        chosen_letters = previous_word

    return (start_or_end, chosen_letters)

def __print_letter(start_or_end, letters, name, is_bot, lives, time_left, message):
    s0 = f"Player {name} {'(Bot)' if is_bot else ''}; ({lives}/3) lives {time_left:.2f} s left!"
    s1 = f"TYPE THE WORD {'STARTING' if start_or_end == LETTER_START else 'ENDING'} WITH"
    s2 = (letters + ("_" * clamp(10 - len(letters), 0, 10))) if start_or_end == LETTER_START else (("_" * clamp(10 - len(letters), 0, 10)) + letters)
    print(s0)
    print("----------------")
    print(s1)
    print(s2)
    print(f"> {'Bot is thinking...' if is_bot else ''}", end="")
    if message:
        print(message)

# returns True if the player manages to get the word in time, False if the player runs out of time
def __player_turn(start_or_end, letters):
    return input().strip().lower()

def __bot_turn(words, start_or_end, letters, bot_difficulty, player_data):
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
    

def destroy(g_ctx):
    del g_ctx["word_bomb"]