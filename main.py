import os

import data.word_bank as word_bank
import data.motd as motd
from common import print_error, safeint

from games.typing_game.main import call as typing_game
from games.minesweeper.main import call as minesweeper
from games.last_letter.main import call as last_letter

def preload_stuff(ctx):
    print("Preloading stuff...")
    
    word_bank_path = os.path.join("data", "english3.txt")
    motd_path = os.path.join("data", "motd.txt")
    
    words = word_bank.try_loading_words(word_bank_path)
    if words is None:
        print_error(f"Cannot load words. \
                    Please make sure the word bank at path {word_bank_path} exists.")
        return False
    ctx["words"] = words
    
    message_of_the_day = motd.get_random_message_of_the_day(motd_path)
    ctx["motd"] = message_of_the_day if message_of_the_day is not None \
        else "(2) Email: You have no new messages today."
    
    print("Yay! Preloading finished!")
    return True

def greet(ctx):
    print()
    print("Hello, user!")
    print(ctx["motd"])
    
def show_games_and_choose(ctx):
    message = ""
    while True:
        print(" ~~~ [Game Selecton] ~~~")
        print("The Typing Game tests your typing skills by you typing words with speed and accuracy!")
        print(" - [1]: Typing Game")
        print(" - [2]: Minesweeper")
        print(" - [3]: Word Bomb")
        print(" - [4]: Math Murder")
        print()
        print(" - [0]: Exit")
        print(message)
        chosen = safeint(input("> "))

        message = ""
        
        if chosen is None:
            message = "Invalid option, try again."
            continue
        
        if chosen == 1:
            typing_game(ctx)
        elif chosen == 2:
            minesweeper(ctx)
        elif chosen == 3:
            last_letter(ctx)
        elif chosen == 4:
            pass
        elif chosen == 0:
            print("BYEEE!!")
            break
        else:
            message = "Invalid option, try again."

def main():
    # global context and variable space for games to use
    global_context = {}    
    success = preload_stuff(global_context)
    if not success:
        print_error("Preloading failed.")
        return
    
    print("*" * 20)
    print()
    
    greet(global_context)
    show_games_and_choose(global_context)


if __name__ == "__main__":
    main()
