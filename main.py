import os
import random
import time

import dialog
import ansi
import terminal
import persistence
from common import print_error, str_to_bool

import procedures
from games.typing_game import typing_game
from games.minesweeper import minesweeper
from games.wordle import wordle
from games.last_letter import last_letter
from status import STATUS_CODE_TO_STRING_TABLE, STATUS_SUCCESS, STATUS_OUT_OF_BOUNDS, STATUS_NEXT, STATUS_PREVIOUS


def init():
    # print(ansi.to_ansi_tokens(ansi.bold(ansi.fgcolor("Hello", terminal.COLOR_BLUE))))
    # input()
    # width = terminal.get_width()
    # height = terminal.get_height()
    # status = terminal.tgfx_draw_rect((width / 2) - 5, (height / 2) - 10, 10, 20)
    # print(STATUS_CODE_TO_STRING_TABLE[status])
    # terminal.tgfx_print_text("the quick brown fox jumped over the lazy dog!", (width / 2) - 5 + 2, (height / 2), 6)
    # print(STATUS_CODE_TO_STRING_TABLE[status])

    # procedure_list = [
    #     procedures.defproc(0, "Exit", None)
    # ]
    # for i in range(1, 100):
    #     procedure_list.append(procedures.defproc(i, f"spam{i}", None))

    # before_header = None
    # offset = 0
    # while True:
    #     status_code, option = procedures.ask_procedure(" ++ Game Selection ++ ",
    #                                                                   "..", procedure_list,
    #                                                                   status_footer=before_header,
    #                                                                   procedure_offset=offset,
    #                                                                   procedure_limit=5)
    #     terminal.put_cursor_to(0, 20)
    #     print(STATUS_CODE_TO_STRING_TABLE[status_code])
    #     if option is None:
    #         continue
    #     if status_code == STATUS_NEXT:
    #         offset += option
    #     elif status_code == STATUS_PREVIOUS:
    #         offset -= option

    # dialog.alert("Hello!", "Dialog", None)

    do_first_time_terminal_init()

    if not terminal.use_advanced_terminal_graphics:
        print("Fancy terminal graphics are disabled!")

def do_first_time_terminal_init():
    status_code, settings = persistence.load_persistence("core")
    if status_code is not STATUS_SUCCESS or settings is None:
        settings = {}

    if not "AdvancedTerminalGfx" in settings:
        terminal.erase_whole_screen()
        terminal.reset_cursor_to_top_left()
    
        print("\nHii! Be honest, do you see a red-background white text in your screen? or just a bunch of garbage?")
        print(ansi.bgcolor(ansi.fgcolor(ansi.bold(" Japan "), terminal.COLOR_WHITE), terminal.COLOR_RED))

        option = input("? (yes or no)> ")
        option = option.lower()

        terminal.use_advanced_terminal_graphics = str_to_bool(option) or option.startswith("ye")
        settings["AdvancedTerminalGfx"] = str(terminal.use_advanced_terminal_graphics)

        dialog.alert("Thank you!! :) You can change this later if you want to switch terminals. Good luck!!", "A thank you letter")

        persistence.save_persistence("core", settings)
    else:
        terminal.use_advanced_terminal_graphics = str_to_bool(settings["AdvancedTerminalGfx"])


# returns the function that returns a function that runs the game
def game_procedure(game_function):
    def the_procedure():
        game = game_function() # creates an instance of the game

        if game["init"]():
            game["run"]()
        else:
            print_error("The game could not be ran.")

        game["destroy"]()

    return the_procedure

def toggle_advanced_tgfx():
    status_code, settings = persistence.load_persistence("core")
    if status_code is not STATUS_SUCCESS or settings is None:
        settings = {}

    settings["AdvancedTerminalGfx"] = str(not terminal.use_advanced_terminal_graphics)
    terminal.use_advanced_terminal_graphics = str_to_bool(settings["AdvancedTerminalGfx"])
    if not terminal.use_advanced_terminal_graphics: # try if it even works lol
        terminal.erase_whole_screen()
        terminal.put_cursor_to(0, 0)
    persistence.save_persistence("core", settings)

    print("\nToggled and changes saved!\n")

def loop():
    procedure_list = [
        procedures.defproc(1, "Typing Game", game_procedure(typing_game)),
        procedures.defproc(2, "Minesweeper", game_procedure(minesweeper)),
        procedures.defproc(3, "Last Letter", game_procedure(last_letter)),
        procedures.defproc(6, "Advanced Terminal Graphics", toggle_advanced_tgfx),
        procedures.defproc(0, "Exit", None)
    ]

    before_header = None
    while True:
        _, option, _ = procedures.ask_procedure(" ++ Game Selection ++ ",
                                             "..", procedure_list,
                                             after_header="Welcome to my 5-in-1 games collection!\n",
                                             status_footer=before_header)
        status_code = procedures.do_execute_procedure(procedure_list, option)
        if status_code != STATUS_SUCCESS:
            before_header = "Invalid option."
            continue
        else:
            before_header = None

        if option == 0: # exit option
            break

def destroy():
    if terminal.use_advanced_terminal_graphics:
        terminal.erase_whole_screen()
        terminal.reset_cursor_to_top_left()
    print("Goodbye!")
    exit()

def main():
    # barebones application framework
    # initialization -> main loop -> destruction
    init()
    loop()
    destroy()

if __name__ == '__main__':
    main()