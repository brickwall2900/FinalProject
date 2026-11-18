import os
import random
import time

import persistence
from common import print_error, str_to_bool

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