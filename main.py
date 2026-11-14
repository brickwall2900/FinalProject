import os
import random
import time

import terminal
from common import print_error

import procedures
from games.typing_game import typing_game
from status import STATUS_CODE_TO_STRING_TABLE, STATUS_SUCCESS, STATUS_OUT_OF_BOUNDS, STATUS_NEXT, STATUS_PREVIOUS


def init():
    # width = terminal.get_width()
    # height = terminal.get_height()
    # status = terminal.tgfx_draw_rect((width / 2) - 5, (height / 2) - 10, 10, 20)
    # print(STATUS_CODE_TO_STRING_TABLE[status])
    # terminal.tgfx_print_text("the quick brown fox jumped over the lazy dog!", (width / 2) - 5 + 2, (height / 2), 6)
    # print(STATUS_CODE_TO_STRING_TABLE[status])

    procedure_list = [
        procedures.defproc(0, "Exit", None)
    ]
    for i in range(1, 100):
        procedure_list.append(procedures.defproc(i, f"spam{i}", None))

    # before_header = None
    # offset = 0
    # while True:
    #     status_code, option = procedures.print_ask_execute_procedures(" ++ Game Selection ++ ",
    #                                                                   "..", procedure_list,
    #                                                                   status_footer=before_header,
    #                                                                   procedure_offset=offset,
    #                                                                   procedure_limit=5)
    #     terminal.put_cursor_to(0, 20)
    #     print(STATUS_CODE_TO_STRING_TABLE[status_code])
    #     if status_code == STATUS_NEXT:
    #         offset += option
    #     elif status_code == STATUS_PREVIOUS:
    #         offset -= option


    if not terminal.use_advanced_terminal_graphics:
        print("Fancy terminal graphics are disabled!")


def game_procedure(game_function):
    def the_procedure():
        game = game_function() # creates an instance of the game

        if game["init"]():
            game["run"]()
        else:
            print_error("The game could not be ran.")

        game["destroy"]()

    return the_procedure

def loop():
    procedure_list = [
        procedures.defproc(1, "Typing Game", game_procedure(typing_game)),
        procedures.defproc(0, "Exit", None)
    ]

    before_header = None
    while True:
        status_code, option = procedures.print_ask_execute_procedures(" ++ Game Selection ++ ",
                                                                      "..", procedure_list,
                                                                      status_footer=before_header)
        if status_code != STATUS_SUCCESS:
            before_header = "Invalid option."
            continue
        else:
            before_header = None

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