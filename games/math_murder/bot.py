import time
import random

from common import *

def __bot_turn(equation, correct_answer, bot_difficulty, player_data):
    # bot difficulty
    # n - initial delay / solve delay / errors / error chance
    # 0 - 7 / 1 / 5 / 1/10
    # 1 - 1 / .5 / 2 / 1/100
    initial_delay = lerp(7, 1, bot_difficulty)
    solve_delay = lerp(1, .5, bot_difficulty)
    errors = lerp(5, 2, bot_difficulty)
    error_chance = int(lerp(10, 100, bot_difficulty))

    error_count = player_data.get("bot_errors", errors)
    
    time.sleep(initial_delay)

    # ok solve
    user_answer = correct_answer
    
    if random.randint(0, error_chance) == 0 and error_count > 0:
        user_answer += random.randint(-100, 100)
        error_count -= 1
        player_data["bot_errors"] = error_count
        time.sleep(random.random() * solve_delay)
        
    return user_answer