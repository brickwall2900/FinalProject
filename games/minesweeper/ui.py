import persistence

import time
import random

from common import safeint, pause, print_error
from games.minesweeper.mscommon import to_coordinate_numbers, to_real_numbers
from games.minesweeper.saveload import __deserialize_board, __deserialize_mines

def __about():
    print("Minesweeper is a game in which you try to discriminate mines out from the board.\n \n" \
            "That is, you correctly identify which is a mine and which is not using inference and logic!", "Minesweeper")

    pause()
    print("This game takes place on an MxN tiles, in which any number of those tiles may contain a mine in them.", "Minesweeper")

    print("Example board:\n \n.2P\n1.1\n. .\n \n" \
    ". is an \"unknown\" tile, meaning you don't know if it is a mine or not.\n" \
    "1-8 tells you the adjacent mines on a tile.\n" \
    "P is a flag. You can place those if you think that tile is a mine.\n", "Minesweeper")

    pause()
    print("IMPORTANT NOTE!! How to play this game on this implementation of Minesweeper:\n" \
                "You are playing in a terminal. That means it might be unconventional for you to " \
                "type to play Minesweeper or other games.\n \n" \
                "Therefore, this version of Minesweeper introduces \"commands\" you can type in-game " \
                "to play the game.", "Minesweeper")

    pause()
    print("IMPORTANT NOTE!! How to play this game on this implementation of Minesweeper:\n \n" \
                "c<r><c> - check mine at <row> <column>; clears neighbors iff they're not mines or they have adjacent mines\n \n" \
                "f<r><c> - toggle flag at <row> <column>", "Minesweeper")

    pause()
    print("IMPORTANT NOTE!! How to play this game on this implementation of Minesweeper:\n \n" \
                "s<r><c> - check mines at a 3x3 radius from the center at <row><column>; " \
                "if not on adjacent mine, does nothing;\n \n" \
                "if on adjacent mine, checks if you've flagged the exact number of adjacent mines then " \
                "checks the not flagged ones.")

    pause()
    print("You LOSE if you check a tile that is a mine.\n"\
                    "You WIN if you check all tiles that is not a mine.\n \n"\
                    "You can read countless tutorials on how to play Minesweeper out there. Good luck and don't die! >:)", "Minesweeper")
    pause()

def __choose_difficulty():
    width, height = None, None

    message = ""
    while True:
        print(" ??? Choose Difficulty ???")
        print(" - [1]: Easy (9x9 tiles)")
        print(" - [2]: Intermediate (16x16 tiles)")
        print(" - [3]: Hard (30x16 tiles)")
        print("... or specify <width>x<height>; like \"20x30\"")
        print()
        print(" - [0]: Exit")
        print(message)
        raw_choice = input("> ").strip()
        chosen = safeint(raw_choice)

        message = ""
        
        if chosen is None:
            dimensions = raw_choice.split("x")
            if len(dimensions) < 2:
                message = "Invalid dimension format."
                continue

            raw_width = dimensions[0]
            raw_height = dimensions[1]

            width = safeint(raw_width)
            height = safeint(raw_height)

            if width is None or height is None:
                message = "Width or height contains a non-number."
            elif not (4 <= width <= 40) or not (4 <= height <= 40):
                message = "Width or height must be in range [4, 40]."
            else:
                break
        
        if chosen == 1:
            width = 9
            height = 9
            break
        elif chosen == 2:
            width = 16
            height = 16
            break
        elif chosen == 3:
            width = 30
            height = 16
            break
        elif chosen == 0:
            break
        else:
            message = "Invalid option, try again."

    return width, height

def __draw_grid(game_context):
    TILE_UNKNOWN        = 0
    TILE_MINE           = -1
    TILE_FLAG           = -2
    TILE_CLEAR          = -3

    game_width = game_context["width"]
    game_height = game_context["height"]

    game_visual_width = game_width + 2
    # 6 because title + border + space + x-numbers + space + border
    game_visual_height = game_height + 6
    game_visual_height -= 1
    for y in range(game_visual_height):
        if y == 0: # title
            print("Minesweeper")
            continue
        elif y == 1 or y == game_visual_height - 1: # border
            print("=" * game_visual_width)
            continue
        elif y == game_visual_height - 2: # bottom space
            print(" ", end="")
            continue
        # else:
        #     print(" ", end="")
        for x in range(game_visual_width):
            if y == 2:
                if x >= 2:
                    print(to_coordinate_numbers(x - 2), end="")
                elif x == 1:
                    print("c", end="")
                elif x == 0:
                    print("r", end="")
            elif y > 2:
                if x == 0:
                    print(to_coordinate_numbers(y - 3), end="")
                elif x > 1:
                    board_value = "?"
                    board = game_context["board"]
                    board_index = (y-3) * game_width + (x-2)
                    board_raw = board[board_index]
                    if board_raw == TILE_UNKNOWN:
                        board_value = "."
                    elif board_raw == TILE_MINE:
                        board_value = "X"
                    elif board_raw == TILE_FLAG:
                        board_value = "P"
                    elif board_raw == TILE_CLEAR:
                        board_value = " "
                    elif 0 <= board_raw and board_raw <= 10:
                        board_value = str(board_raw)
                    print(board_value, end="")
                else:
                    print(" ", end="")
            # else:
                # print(" ", end="")    
        print("")



def __user_input(game_context):
    print("TIME :")
    print(f"{game_context['time']:.2f} secs")
    print(" ")
    print("FLAGS:")
    print(f" {game_context['flag_count'] if game_context['flag_count'] is not None else '???'} flags")
    print(" ")
    print("Commands:")
    print("  * x<r><c>")
    print("  checks for a mine")
    print("  * f<r><c>")
    print("  puts down a flag")
    print("  * s<r><c>")
    print("  checks for mines in 3x3 area iff adj tiles are OK (flagged)")
    print("  * /exit")
    print("  closes the game")
    print("Command: ", end="")
    return input()

def __print_congrats(game_context):
    from games.minesweeper.leaderboards import __save_to_leaderboard
    
    persistence.remove_persistence("minesweeper")

    submitted = False
    message = ""
    time_taken = game_context["time"]
    while True:
        print("~~~^ CONGRATULATIONS ^~~~")
        print(f"Congratulations! You took {time_taken:.2f} seconds to find all mines.")

        print(" - [1] Submit to Leaderboard")
        print()
        print(" - [0]: Exit")
        print(message)

        chosen = safeint(input("> "))
        message = ""
        if chosen is None:
            message = "Invalid option, try again."
            continue

        if chosen == 2 and not submitted:
            __save_to_leaderboard(game_context)
            submitted = True
        elif chosen == 0:
            break
        else:
            message = "Invalid option, try again."

def __view_dead_board(game_context, mines_raw, board_raw, time, width, height):
    mines = __deserialize_mines(mines_raw)
    board = __deserialize_board(board_raw)

    if mines is None:
        print_error("Cannot parse mines data")
        return

    if board is None:
        print_error("Cannot parse board data")
        return

    copy_game_context = game_context.copy()
    copy_game_context["dead"] = True
    copy_game_context["board"] = board
    copy_game_context["flag_count"] = 0
    copy_game_context["mines"] = mines
    copy_game_context["time"] = time
    copy_game_context["width"] = width
    copy_game_context["height"] = height

    running = True
    while running:
        __draw_grid(copy_game_context)
        command = __user_input(copy_game_context)
        if command.lower().strip() == "/exit":
            running = False
        