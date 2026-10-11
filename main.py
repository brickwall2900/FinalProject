import os
import random
import time

import terminal
from common import print_error

from games.base_game import BaseGame
from games.typing_game import TypingGame

import procedures
from status import STATUS_CODE_TO_STRING_TABLE


def init():
    pass

def game_procedure(game_class):
    def the_procedure():
        game = game_class()

        if game.init():
            game.run()
        else:
            print_error("The game could not be ran.")

        game.destroy()

    return the_procedure

def loop():
    procedure_list = [
        procedures.defproc(1, "Typing Game", game_procedure(TypingGame)),
        procedures.defproc(0, "Exit", None)
    ]

    while True:
        procedures.print_procedures(" ++ Game Selection ++ ", "..", procedure_list)
        success, option = procedures.ask_and_execute_procedure(procedure_list)
        if not success:
            print("Invalid option")
            continue

        if option == 0: # exit option
            break

def destroy():
    terminal.erase_whole_screen()
    terminal.reset_cursor_to_top_left()
    print("Goodbye!")
    exit()

def main():
    # barebones application framework
    # initialization -> main loop -> destruction
    terminal.erase_whole_screen()
    terminal.reset_cursor_to_top_left()
    init()
    loop()
    destroy()

if __name__ == '__main__':
    main()