import time
import random

from common import *
from games.math_murder.ui import __about, __print_letter, __show_leaderboard
from games.math_murder.bot import __bot_turn

# inspired by that one ropblox game i played

def call(unused):
    run()

def run():
    message = ""
    while True:
        print(" ~~~ [!] Math Murder [!] ~~~")
        print("Math Murder is a multiplayer game, testing your quick math skills! Last one alive wins.")
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
    LETTER_START        = 0
    LETTER_END          = 1

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

# returns tuple (<equation>, <correct answer>)
def __build_next_equation(equation, prev_correct_answer):
    