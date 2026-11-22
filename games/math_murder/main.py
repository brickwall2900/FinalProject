import time
import random

from common import *
from games.math_murder.ui import __about, __print_equation, __show_leaderboard
from games.math_murder.bot import __bot_turn

# inspired by that one ropblox game i played

def call(_unused):
    run()

def run():
    message = ""
    while True:
        print("\x1b[37;41m ~~~ [!] Math Murder [!] ~~~ \x1b[0m")
        print("\x1b[37mMath Murder is a multiplayer game, testing your quick math skills! Last one alive wins.\x1b[0m")
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
            game()
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

def game():
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

    print("\x1b[37mYou can either have two or more keyboards connected to the same computer albeit with sabotage... OR share one keyboard... albeit with contention.\x1b[0m")
    print()

    print(f"\x1b[37;1mPlayers: \x1b[2m{__count(players, False)}\x1b[22m / Bots: \x1b[2m{__count(players, True)}\x1b[0m")
    ready = yes_or_no("Are y'all ready")
    if not ready:
        print("\x1b[33mOkay; someone is not ready...\x1b[0m")
        return

    __core_game_loop(players)

def __core_game_loop(players):
    previous_answer = None
    rounds = 0
    time_seconds = 10
    prev_player_finish_time = None
    message = None
    ranking = len(players)

    while ranking > 1:
        for player in players:
            if ranking <= 1:
                break

            if player["lives"] <= 0:
                continue

            # pick a letter first
            equation, correct_answer = __build_next_equation(previous_answer, rounds)

            name = player["name"]
            is_a_bot = not player["real"]

            judge_timestamp = time.time()
            yay = False
            while True: # turn would not end until player gets a correct word
                if player["lives"] <= 0:
                    break

                __print_equation(equation, name, is_a_bot, player["lives"], time_seconds - (time.time() - judge_timestamp), message)

                user_answer = None
                if is_a_bot:
                    time.sleep(.5)
                    user_answer = __bot_turn(equation, correct_answer, player["bot_skill"], player)
                    print()
                else:
                    user_answer = safeint(input().strip().lower())

                time_taken = (time.time() - judge_timestamp)
                if time_taken > time_seconds: # timed out
                    message = f"{name} timed out!\nThe answer was {correct_answer} if anyone was wondering."
                    previous_answer = (previous_answer if previous_answer is not None else 2) // (rounds if rounds > 0 else 1)
                    break

                # judge time
                if user_answer == correct_answer and user_answer is not None:
                    player["score"] += get_whole_digits(correct_answer) * 50
                    yay = True
                    prev_player_finish_time = time_taken
                    previous_answer = correct_answer
                    message = f"{name} took {prev_player_finish_time:.2f} seconds to finish!"
                    break
                else:
                    message = "Your answer is not correct. "

            if not yay: # nay
                player["lives"] -= 1

            if player["lives"] <= 0:
                message = f"Uh-oh! {name} ran out of lives and lost..."
                player["ranking"] = ranking
                ranking -= 1
                
        rounds += 1

    # last one standing wins rank 1
    for player in players:
        if "ranking" not in player:
            player["ranking"] = 1

    __show_leaderboard(players)
    
def __get_factors(number):
    factors = []
    for possible_factor in range(number - 1, 0, -1):
        if number % possible_factor == 0:
            factors.append(possible_factor)
            
    return factors

# returns tuple (<equation>, <correct answer>)
def __build_next_equation(prev_correct_answer, rounds):
    OP_ADD              = 0
    OP_MULTIPLY         = 1
    OP_DIVIDE           = 2
    OP_REMINDER         = 3
    
    random.seed()
    
    max_number = lerp(10, 500, max(0, (rounds - 100) / 100))
    
    if prev_correct_answer is None:
        prev_correct_answer = random.randint(-max_number, max_number)
    
    max_operation = OP_ADD
    if rounds > 10:
        max_operation = OP_MULTIPLY
    if rounds > 30:
        factors = __get_factors(prev_correct_answer)
        allowed_factors = [f for f in factors if f < max_number]
        if len(allowed_factors) > 1:
            max_number = OP_DIVIDE
    if rounds > 60:
        max_number = OP_REMINDER
    
    equation = str(prev_correct_answer)
        
    operation_used = random.randint(OP_ADD, max_operation)
    
    if operation_used == OP_ADD:
        added_number = random.randint(-max_number, max_number)
        prev_correct_answer += added_number
        is_negative = added_number < 0
        equation = equation + " " + ("-" if is_negative else "+") + " " + str(added_number)[(1 if is_negative else 0):]
    elif operation_used == OP_MULTIPLY:
        multiplied_number = random.randint(-max_number // 2, max_number // 2)
        prev_correct_answer *= multiplied_number
        is_negative = multiplied_number < 0
        equation = equation + " x " + str(multiplied_number)
    elif operation_used == OP_DIVIDE:
        factors = __get_factors(prev_correct_answer)
        allowed_factors = [f for f in factors if f < max_number]
        divided_by = random.choice(allowed_factors)
        divided_by = -divided_by if randbool() else divided_by
        prev_correct_answer /= divided_by
        is_negative = divided_by < 0
        equation = equation + " / " + str(divided_by)
    elif operation_used == OP_REMINDER:
        divided_by = random.randint(-max_number // 2, max_number // 2)
        prev_correct_answer = prev_correct_answer % divided_by
        is_negative = divided_by < 0
        equation = equation + " % " + str(divided_by)
        
    return equation, prev_correct_answer
        