from data import word_bank

import time
import random

from common import *
from games.last_letter.ui import __about, __print_letter, __show_leaderboard
from games.last_letter.bot import __bot_turn

# inspired by that one ropblox game i played

def call(g_ctx):
    run(g_ctx)

def run(g_ctx):
    words = g_ctx["words"]

    message = ""
    while True:
        print("\x1b[30;43m ~~~ [!] Word Bomb [!] ~~~\x1b[0m")
        print("\x1b[37mWord Bomb is a multiplayer game. Come up with words that have the first or last letter! Last one standing alive wins.\x1b[0m")
        print("\x1b[1m - [1]: PLAY!!!\x1b[0m")
        print("\x1b[1m - [2]: About\x1b[0m")
        print()
        print("\x1b[1m - [0]: Exit\x1b[0m")
        print(f"\x1b[33m{message!s}\x1b[0m")
        chosen = safeint(input("> "))

        message = ""
        
        if chosen is None:
            message = "Invalid option, try again."
            continue
        
        if chosen == 1:
            game(words)
        elif chosen == 2:
            __about()
        elif chosen == 0:
            break
        else:
            message = "Invalid option, try again."

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

def game(words):
    players = [] # a list of dicts (player data)

    number_of_players = None
    while number_of_players is None:
        number_of_players_raw = input("Give the number of players that will be playing: ")
        number_of_players = safeint(number_of_players_raw)
        if number_of_players is not None and number_of_players < 2:
            print_error("Cannot have less than two players.")
            number_of_players = None # whoops
        elif number_of_players is None:
            print_error("Invalid player count.")

    for id in range(number_of_players):
        players.append(__setup_player(id))

    print("\x1b[37mYou can either have two or more keyboards connected to the same computer albeit with sabotage...OR share one keyboard... albeit with contention.\x1b[0m")
    print()

    print(f"\x1b[37;1mPlayers: \x1b[2m{__count(players, False)}\x1b[22m / Bots: \x1b[2m{__count(players, True)}\x1b[0m")
    ready = yes_or_no("Are y'all ready")
    if not ready:
        print("\x1b[33mOkay; someone is not ready...\x1b[0m")
        return

    __core_game_loop(players, words)

def __core_game_loop(players, words):
    LETTER_START        = 0
    LETTER_END          = 1

    previous_word = None
    time_seconds = 10
    rounds = 0
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
            start_or_end, letters = __pick_letter(words, previous_word, rounds)

            name = player["name"]
            is_a_bot = not player["real"]

            judge_timestamp = time.time()
            yay = False
            while True: # turn would not end until player gets a correct word
                if player["lives"] <= 0:
                    break

                __print_letter(start_or_end, letters, name, is_a_bot, player["lives"], time_seconds - (time.time() - judge_timestamp), time_seconds, message)

                word = None
                if is_a_bot:
                    time.sleep(1)
                    word = __bot_turn(words, start_or_end, letters, player["bot_skill"], player)
                else:
                    word = input().strip().lower()

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
                    
                    if word is not None and len(word) > 0:
                        previous_word = word
                    else:
                        previous_word = None
                        
                    break
                elif word is not None:
                    # player["lives"] -= 1
                    # unfair?
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
                
        rounds += 1
        if (20 - rounds) >= 0:
            time_seconds = lerp(5, 10, max(1, (rounds - 20) / 100))

    # last one standing wins rank 1
    for player in players:
        if "ranking" not in player:
            player["ranking"] = 1

    __show_leaderboard(players)

# returns tuple (LETTER_START | LETTER_END, <chars>)
def __pick_letter(words, previous_word, round):
    LETTER_START        = 0
    LETTER_END          = 1
    start_or_end = LETTER_START if randbool() else LETTER_END
    
    random.seed()

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
        max_i = 0
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
    if round < 20:
        chosen_letter_count = chars_to_slice_list[min(chosen_letter_count_idx[0] - 1, 0)]
    
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