import persistence

import time
import random

from common import safeint, pause, print_error
from games.minesweeper.mscommon import to_coordinate_numbers, to_real_numbers
from games.minesweeper.saveload import __deserialize_board, __deserialize_mines

def __about():
    print("\x1b[37mMinesweeper is a game in which you try to discriminate mines out from the board.\x1b[0m")
    print()
    print("\x1b[37mThat is, you correctly identify which is a mine and which is not using inference and logic!\x1b[0m")

    pause()
    print("\x1b[37mThis game takes place on an MxN tiles, in which any number of those tiles may contain a mine in them.\x1b[0m")

    print("\x1b[37mExample board:\n \n.\x1b[33m2\x1b[32;1mP\n\x1b[33;22m1\x1b[37m.\x1b[33m1\n\x1b[37m. .\n \n. is an \"unknown\" tile, meaning you don't know if it is a mine or not.\x1b[0m")
    print("\x1b[33m1-8\x1b[37m tells you the adjacent mines on a tile.\x1b[0m")
    print("\x1b[32;1mP\x1b[37;22m is a flag. You can place those if you think that tile is a mine.\x1b[0m")

    pause()
    print("\x1b[37;1mIMPORTANT NOTE!! How to play this game on this implementation of Minesweeper:\x1b[0m")
    print("\x1b[37;1mYou are playing in a terminal. That means it might be unconventional for you to type to play Minesweeper or other games.\x1b[0m")
    print()
    print("\x1b[37mTherefore, this version of Minesweeper introduces \"commands\" you can type in-game to play the game.\x1b[0m")

    pause()
    print("\x1b[37;1mIMPORTANT NOTE!! How to play this game on this implementation of Minesweeper:\x1b[0m")
    print()
    print("\x1b[37mc<r><c> - check mine at <row> <column>; clears neighbors iff they're not mines or they have adjacent mines\x1b[0m")
    print()
    print("\x1b[37mf<r><c> - toggle flag at <row> <column>", "Minesweeper\x1b[0m")

    pause()
    print("\x1b[37;1mIMPORTANT NOTE!! How to play this game on this implementation of Minesweeper:\x1b[0m")
    print()
    print("\x1b[37ms<r><c> - check mines at a 3x3 radius from the center at <row><column>; if not on adjacent mine, does nothing;\x1b[0m")
    print()
    print("\x1b[37mif on adjacent mine, checks if you've flagged the exact number of adjacent mines then checks the not flagged ones.\x1b[0m")

    pause()
    print("\x1b[37mYou \x1b[31;1mLOSE\x1b[37m if you check a tile that is a mine.\x1b[0m")
    print("\x1b[37mYou \x1b[32;1mWIN\x1b[37m if you check all tiles that is not a mine.\x1b[0m")
    print()
    print("\x1b[92mYou can read countless tutorials on how to play Minesweeper out there. Good luck and don't die! >:)\x1b[0m")
    pause()

def __choose_difficulty():
    width, height = None, None

    message = ""
    while True:
        print("\x1b[30;47m ??? Choose Difficulty ??? \x1b[0m")
        print("\x1b[1m - [1]: Easy (9x9 tiles)\x1b[0m")
        print("\x1b[1m - [2]: Intermediate (16x16 tiles)\x1b[0m")
        print("\x1b[1m - [3]: Hard (30x16 tiles)\x1b[0m")
        print("\x1b[2m... or specify <width>x<height>; like \"20x30\"\x1b[0m")
        print()
        print("\x1b[1m - [0]: Exit\x1b[0m")
        print(f"\x1b[33m{message}\x1b[0m")
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
            print("\x1b[30;42;1;4mMinesweeper\x1b[0m")
            continue
        elif y == 1 or y == game_visual_height - 1: # border
            print(f"\x1b[37m{'=' * game_visual_width!s}\x1b[0m")
            continue
        elif y == game_visual_height - 2: # bottom space
            print("\x1b[37m \x1b[0m", end="")
            continue
        # else:
        #     print(" ", end="")
        for x in range(game_visual_width):
            if y == 2:
                if x >= 2:
                    print(f"\x1b[37m{to_coordinate_numbers(x - 2)} \x1b[0m", end="")
                elif x == 1:
                    print("\x1b[37;1;5mc\x1b[0m", end="")
                elif x == 0:
                    print("\x1b[37;1;5mr\x1b[0m", end="")
            elif y > 2:
                if x == 0:
                    print(f"\x1b[37m{to_coordinate_numbers(y - 3)}\x1b[0m", end="")
                elif x > 1:
                    board_value = "?"
                    board = game_context["board"]
                    board_index = (y-3) * game_width + (x-2)
                    board_raw = board[board_index]
                    if board_raw == TILE_UNKNOWN:
                        board_value = "\x1b[37m.\x1b[0m"
                    elif board_raw == TILE_MINE:
                        board_value = "\x1b[37;41;5;1mX\x1b[0m"
                    elif board_raw == TILE_FLAG:
                        board_value = "\x1b[32;1mP\x1b[0m"
                    elif board_raw == TILE_CLEAR:
                        board_value = "\x1b[37m \x1b[0m"
                    elif 0 <= board_raw and board_raw <= 10:
                        board_value = str(board_raw)
                    print(f"\x1b[37m{board_value} \x1b[0m", end="")
                else:
                    print("\x1b[37m \x1b[0m", end="")
            # else:
                # print(" ", end="")    
        print()

def __user_input(game_context):
    print(f"\x1b[37;4;1mTIME \x1b[21;24m: {game_context['time']:.2f} secs\x1b[0m")
    print(f"\x1b[37;4;1mFLAGS\x1b[24m: {(game_context['flag_count'] if game_context['flag_count'] is not None else '???')} flags\x1b[0m")
    print("\x1b[37;4;1mCommands:\x1b[0m")
    print("\x1b[37;1m  * x<r><c> <-\x1b[2m checks for a mine\x1b[0m")
    print("\x1b[37;1m  * f<r><c> <-\x1b[2m puts down a flag\x1b[0m")
    print("\x1b[37;1m  * s<r><c> <-\x1b[2m checks for mines in 3x3 area iff adj tiles are OK (flagged)\x1b[0m")
    print("\x1b[37;1m  * /exit   <-\x1b[2m closes the game\x1b[0m")
    print("\x1b[37;1mCommand: \x1b[0m", end="")
    return input()

def __print_congrats(game_context):
    from games.minesweeper.leaderboards import __save_to_leaderboard
    
    persistence.remove_persistence("minesweeper")

    submitted = False
    message = ""
    time_taken = game_context["time"]
    while True:
        print("\x1b[30;43m ~~~^ CONGRATULATIONS ^~~~ \x1b[0m")
        print(f"\x1b[37mCongratulations! You took \x1b[32m{time_taken:.2f} seconds to find all mines.\x1b[0m")

        print("\x1b[1m - [1] Submit to Leaderboard\x1b[0m")
        print()
        print("\x1b[1m - [0]: Exit\x1b[0m")
        print(f"\x1b[33m{message}\x1b[0m")

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
        