from status import *

import procedures
import dialog
import terminal
import ansi
import persistence

import time
import random

from common import safeint, print_error, get_digits, clamp, find, safefloat, sort, str_to_bool
# yay i'm realy proud of this
TILE_UNKNOWN        = 0
TILE_MINE           = -1
TILE_FLAG           = -2
TILE_CLEAR          = -3

def minesweeper():
    game_context = {}
    running = False

    def init():
        return True

    def run():
        procedures_list = [
            procedures.defproc(1, "Start", game),
            procedures.defproc(2, "Leaderboards", __view_leaderboard),
            procedures.defproc(3, "About/Information", __about),
            procedures.defproc(0, "Exit", None)
        ]

        status_footer = None
        procedure_offset = 0
        while True:
            status_code, option, _ = procedures.ask_procedure("Minesweeper!!", "[*][]",
                                                                            procedures_list,
                                                                            status_footer=status_footer,
                                                                            after_header="Minesweeper is a game where you avoid mines... Don't get blown up!",
                                                                            procedure_offset=procedure_offset)

            if status_code == STATUS_NEXT and option is not None:
                procedure_offset += option
                continue
            elif status_code == STATUS_PREVIOUS and option is not None:
                procedure_offset -= option
                continue
            
            status_code = procedures.do_execute_procedure(procedures_list, option)
            if status_code != STATUS_SUCCESS:
                status_footer = "Invalid option."
                continue
            else:
                status_footer = None

            if option == 0:  # exit option
                break

    def __about():
        dialog.alert("Minesweeper is a game in which you try to discriminate mines out from the board.\n \n" \
                "That is, you correctly identify which is a mine and which is not using inference and logic!", "Minesweeper")

        dialog.alert("This game takes place on an MxN tiles, in which any number of those tiles may contain a mine in them.", "Minesweeper")

        dialog.alert("Example board:\n \n.2P\n1.1\n. .\n \n" \
        ". is an \"unknown\" tile, meaning you don't know if it is a mine or not.\n" \
        "1-8 tells you the adjacent mines on a tile.\n" \
        "P is a flag. You can place those if you think that tile is a mine.\n", "Minesweeper")

        dialog.alert("IMPORTANT NOTE!! How to play this game on this implementation of Minesweeper:\n" \
                    "You are playing in a terminal. That means it might be unconventional for you to " \
                    "type to play Minesweeper or other games.\n \n" \
                    "Therefore, this version of Minesweeper introduces \"commands\" you can type in-game " \
                    "to play the game.", "Minesweeper")

        dialog.alert("IMPORTANT NOTE!! How to play this game on this implementation of Minesweeper:\n \n" \
                    "c<r><c> - check mine at <row> <column>; clears neighbors iff they're not mines or they have adjacent mines\n \n" \
                    "f<r><c> - toggle flag at <row> <column>", "Minesweeper")

        dialog.alert("IMPORTANT NOTE!! How to play this game on this implementation of Minesweeper:\n \n" \
                    "s<r><c> - check mines at a 3x3 radius from the center at <row><column>;" \
                    "if not on adjacent mine, does nothing;\n \n" \
                    "if on adjacent mine, checks if you've flagged the exact number of adjacent mines then" \
                    "checks the not flagged ones.")

        dialog.alert("You LOSE if you check a tile that is a mine.\n"\
                     "You WIN if you flag all tiles that is a mine.\n \n"\
                     "You can read countless tutorials on how to play Minesweeper out there. Good luck and don't die! >:)", "Minesweeper")

    def __choose_difficulty():
        dwidth, dheight = None, None
        def __predefined(width, height):
            def _proc():
                nonlocal dwidth, dheight
                dwidth, dheight = width, height

            return _proc

        def __custom():
            def _proc():
                nonlocal dwidth, dheight
                width = None
                height = None
                while True:
                    tmp = dialog.input("Specify width", "Minesweeper - Custom Difficulty")
                    width = safeint(tmp)
                    if width is None:
                        print_error("Bad width input")
                        continue
                    if width < 4 or width > 30:
                        print_error("Width is out of range (not 4 < width < 30)")
                        continue
                    break
                while True:
                    tmp = dialog.input("Specify height", "Minesweeper - Custom Difficulty")
                    height = safeint(tmp)
                    if height is None:
                        print_error("Bad height input")
                        continue
                    if height < 4 or height > 30:
                        print_error("Height is out of range (not 4 < height < 30)")
                        continue
                    break
                dwidth, dheight = width, height
            return _proc

        procedures_list = [
            procedures.defproc(1, "Easy - 9x9 cells", __predefined(9, 9)),
            procedures.defproc(2, "Medium - 16x16 cells", __predefined(16, 16)),
            procedures.defproc(3, "Hard - 30x16 cells", __predefined(30, 16)),
            procedures.defproc(4, "Custom", __custom())
        ]

        status_footer = None
        procedure_offset = 0
        while True:
            status_code, option, _ = procedures.ask_procedure("Difficulty Select", "#",
                                                                            procedures_list,
                                                                            status_footer=status_footer,
                                                                            procedure_offset=procedure_offset)

            if status_code == STATUS_NEXT and option is not None:
                procedure_offset += option
                continue
            elif status_code == STATUS_PREVIOUS and option is not None:
                procedure_offset -= option
                continue
            
            status_code = procedures.do_execute_procedure(procedures_list, option)
            if status_code != STATUS_SUCCESS:
                status_footer = "Invalid option."
                continue
            else:
                status_footer = None
                break

        return dwidth, dheight

    def __new_game():
        width, height = __choose_difficulty()
        game_context["width"] = width
        game_context["height"] = height

        assert width and height

        game_context["dead"] = False
        game_context["time"] = 0

        # visual boards
        game_context["board"] = [TILE_UNKNOWN] * (width * height)
        game_context["mines"] = [] # tuples of positions
        game_context["flag_count"] = None
        game_context["dirty"] = False # if the board is modified before the game is saved

    def __save_game():
        serialized_game_context = game_context.copy()
        serialized_game_context["board"] = __serialize_board(serialized_game_context["board"])
        serialized_game_context["mines"] = __serialize_mines(serialized_game_context["mines"])
        serialized_game_context["dirty"] = "False"
        status_code = persistence.save_persistence("minesweeper", serialized_game_context)
        return status_code

    def __load_game():
        nonlocal game_context
        status_code, loaded_game_context = persistence.load_persistence("minesweeper")
        if status_code != STATUS_SUCCESS or loaded_game_context is None:
            if status_code != STATUS_FILE_NOT_FOUND:
                print_error("The save file could not be loaded. Starting a new game instead.")
            return False

        options = ["Yes, load it!", "No.. do NOT load it!!"]
        if dialog.alert("Save file found. Continue last game?", "Minesweeper", options, options[0]) == options[1]:
            return False

        loaded_game_context["width"] = safeint(loaded_game_context["width"])
        loaded_game_context["height"] = safeint(loaded_game_context["height"])

        loaded_game_context["dead"] = str_to_bool(loaded_game_context["dead"])
        loaded_game_context["time"] = safefloat(loaded_game_context["time"])

        # visual boards
        st, loaded_game_context["board"] = __deserialize_board(loaded_game_context["board"])
        if st != STATUS_SUCCESS:
            print_error("Board cannot be read...")
        st, loaded_game_context["mines"] = __deserialize_mines(loaded_game_context["mines"])
        if st != STATUS_SUCCESS:
            print_error("Mine data cannot be read...")
        loaded_game_context["flag_count"] = safeint(loaded_game_context["flag_count"])
        loaded_game_context["dirty"] = str_to_bool(loaded_game_context["dirty"])

        # as a failsafe
        if loaded_game_context["width"] is None \
            or loaded_game_context["height"] is None \
            or loaded_game_context["dead"] is None \
            or loaded_game_context["time"] is None \
            or loaded_game_context["board"] is None \
            or loaded_game_context["mines"] is None \
            or loaded_game_context["flag_count"] is None \
            or loaded_game_context["dirty"] is None:
            print_error("Save file seems to be corrupt... Starting a new game instead. :\\")
            return False

        game_context = loaded_game_context
        return True

    def game():
        nonlocal running

        if not __load_game():
            __new_game()

        running = True
        while running:
            t = time.time()
            __draw_grid()
            __user_input()
            dt = time.time() - t
            if len(game_context["mines"]) > 0 and not game_context["dead"]:
                if "tracking_time" in game_context:
                    game_context["time"] = game_context["time"] + dt
                else:
                    game_context["tracking_time"] = True

    def __draw_grid():
        game_width = game_context["width"]
        game_height = game_context["height"]

        game_visual_width = game_width + 2
        # 6 because title + border + space + x-numbers + space + border
        game_visual_height = game_height + 6
        if terminal.use_advanced_terminal_graphics:
            terminal.erase_whole_screen()
            viewport_width = terminal.get_width()
            viewport_height = terminal.get_height()

            board_x = ((viewport_width - (game_visual_width + 30)) / 2)
            board_y = (viewport_height - game_visual_height) / 2

            # draw row to column
            for y in range(game_visual_height):
                if y == 0: # title
                    terminal.tgfx_print_text("Minesweeper", board_x + game_visual_width / 2 - terminal.get_string_visual_width("Minesweeper") / 2, board_y + y)
                    continue
                elif y == 1 or y == game_visual_height - 1: # border
                    terminal.tgfx_print_text("=" * game_visual_width, board_x, board_y + y)
                    continue
                elif y == 2:
                    terminal.tgfx_print_text("r/c", board_x, board_y + y)
                    continue
                elif y == game_visual_height - 2: # bottom space
                    continue

                for x in range(game_visual_width):
                    # terminal.tgfx_print_text("?", x + board_x, y + board_y)
                    
                    if y == 3 and x >= 2:
                        terminal.tgfx_print_text(__to_coordinate_numbers(x - 2), x + board_x, y + board_y)
                    elif y > 3:
                        if x == 0:
                            terminal.tgfx_print_text(__to_coordinate_numbers(y - 4), x + board_x, y + board_y)
                        elif x > 1:
                            board_value = "?"
                            board = game_context["board"]
                            board_index = (y-4) * game_width + (x-2)
                            board_raw = board[board_index]
                            if board_raw == TILE_UNKNOWN:
                                board_value = "."
                            elif board_raw == TILE_MINE:
                                board_value = ansi.bgcolor(ansi.fgcolor("X", terminal.COLOR_WHITE), terminal.COLOR_RED)
                            elif board_raw == TILE_FLAG:
                                board_value = ansi.fgcolor("P", terminal.COLOR_GREEN)
                            elif board_raw == TILE_CLEAR:
                                board_value = " "
                            elif 0 <= board_raw and board_raw <= 10:
                                board_value = ansi.fgcolor(str(board_raw), terminal.COLOR_YELLOW)
                            terminal.tgfx_print_text(board_value, x + board_x, y + board_y)

    REAL_TO_COORDINATE_VALUES = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                                 "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
                                 "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                                 "u", "v", "w", "x", "y", "z", "@", "#", "$", "&"]
    def __to_coordinate_numbers(real):
        if real >= len(REAL_TO_COORDINATE_VALUES) or real < 0:
            return "?"

        return REAL_TO_COORDINATE_VALUES[real]

    def __to_real_numbers(coordinate):
        for real in range(len(REAL_TO_COORDINATE_VALUES)):
            if coordinate == REAL_TO_COORDINATE_VALUES[real]:
                return real

        return None

    def __user_input():
        rect_width = 30
        # 6 because title + border + space + x-numbers + space + border
        rect_height = max(game_context["height"] + 6, 20)
        if terminal.use_advanced_terminal_graphics:
            viewport_width = terminal.get_width()
            viewport_height = terminal.get_height()

            if not terminal.tgfx_warn_no_space(rect_width + game_context["width"] + 3):
                input() # wait for user input
                return

            ctrls_x = ((viewport_width - ((game_context["width"] + 2) + rect_width)) / 2) + (game_context["width"] + 2) + 2
            ctrls_y = (viewport_height - rect_height) / 2
            terminal.tgfx_draw_rect(ctrls_x, ctrls_y, rect_width, rect_height, char="*") 

            def puts(text, x, y):
                terminal.tgfx_print_text(text, x, y, rect_width-2, True)
                status_code, lines = terminal.get_wrap_lines(text, rect_width-2, True)
                assert(status_code == STATUS_SUCCESS)
                return lines

            text_x = ctrls_x+2
            text_y = ctrls_y+1
            text_y += puts("TIME :", text_x, text_y)
            text_y += puts(f"{game_context["time"]:.2f} secs", text_x, text_y)
            text_y += puts(" ", text_x, text_y)
            text_y += puts("FLAGS:", text_x, text_y)
            text_y += puts(f" {game_context["flag_count"] if game_context["flag_count"] is not None else "???"} flags", text_x, text_y)
            text_y += puts(" ", text_x, text_y)
            # text_y += puts(" ", text_x, text_y)
            text_y += puts("Commands:", text_x, text_y)
            text_y += puts("  * x<r><c>", text_x, text_y)
            text_y += puts("  checks for a mine", text_x, text_y)
            text_y += puts("  * f<r><c>", text_x, text_y)
            text_y += puts("  puts down a flag", text_x, text_y)
            text_y += puts("  * s<r><c>", text_x, text_y)
            text_y += puts("  checks for mines in 3x3 area iff adj tiles are OK (flagged)", text_x, text_y)
            text_y += puts("  * /exit", text_x, text_y)
            text_y += puts("  closes the game", text_x, text_y)
            text_y += puts("Command: ", text_x, text_y)
            command = input()
            __process_command(command)

    def __process_command(command):
        nonlocal running

        is_game_over = game_context["dead"]

        command = str(command).lower().strip()
        if command == "/exit":
            # ??? profit?
            # wait wtf"?
            if not is_game_over:
                options = ["Yes!", "No...", "Cancel"]
                if game_context["dirty"]:
                    user_option = dialog.alert("Game board is modified. Save game?", "Minesweeper", options, options[0])
                    if user_option == options[2]:
                        return
                    elif user_option == options[0]:
                        status_code = __save_game()
                        if status_code != STATUS_SUCCESS:
                            print_error(f"The game could not be saved: {STATUS_CODE_TO_STRING_TABLE[status_code]}")
                            return
            running = False

        if (command.startswith("x") or command.startswith("f") or command.startswith("s")) and not is_game_over:
            if len(command) < 3:
                print_error("Position x AND y is required.")
                return
            
            pos_x, pos_y = __to_real_numbers(command[2]), __to_real_numbers(command[1])

            bad_x, bad_y = pos_x is None, pos_y is None
            if bad_x or bad_y:
                print_error(f"Invalid {"x and y" if bad_x and bad_y else "x" if bad_x else "y"} position.")
                return

            game_width = game_context["width"]
            game_height = game_context["height"]

            assert pos_x is not None and pos_y is not None

            bad_x = pos_x > game_width - 1 or pos_x < 0
            bad_y = pos_y > game_height - 1 or pos_y < 0
            if bad_x or bad_y:
                print_error(f"{"x and y position" if bad_x and bad_y else "x-position" if bad_x else "y-position"} is out of bounds")
                return

            mines = game_context["mines"]
            tiles = game_context["board"]
            first_click = len(mines) == 0
            current_tile_index = pos_y * game_width + pos_x
            current_tile = tiles[current_tile_index]

            def check_tile(x, y):
                tile_index = y * game_width + x
                tile = tiles[tile_index]
                if tile == TILE_FLAG:
                    return

                # check if pos is a mine
                if find(mines, (x, y)) is not None:
                    # game over lol
                    game_context["dead"] = True
                    persistence.remove_persistence("minesweeper")
                    dialog.alert("YOU LOST! ;(", "Minesweeper")
                    for mx, my in mines:
                        tiles[my * game_width + mx] = TILE_MINE
                    return

                # okay so if not a mine
                # do shit

                __find_not_mines_algorithm(tiles, mines, x, y, game_width, game_height, tile_index)

            if command.startswith("x"):
                # okay
                # check for first click
                if first_click:
                    # if first click, generate mines
                    number_of_tiles = game_width * game_height
                    number_of_mines = int(number_of_tiles * (random.random() / 20 + .10))
                    first_click_safety = []
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            cx, cy = pos_x+i, pos_y+j
                            # ensure in bounds
                            if cx >= 0 and cx < game_width and cy >= 0 and cy < game_height:
                                first_click_safety.append((cx, cy))
                    __generate_mines(mines, game_width, game_height, number_of_mines, first_click_safety)
                    game_context["flag_count"] = number_of_mines

                check_tile(pos_x, pos_y)
            elif command.startswith("s") and not first_click:
                if current_tile <= 0:
                    return

                flag_count = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        cx, cy = pos_x+i, pos_y+j
                        # ensure in bounds
                        if cx >= 0 and cx < game_width and cy >= 0 and cy < game_height and tiles[cy * game_width + cx] == TILE_FLAG:
                            flag_count += 1

                if flag_count != current_tile:
                    return

                for i in range(-1, 2):
                    for j in range(-1, 2):
                        cx, cy = pos_x+i, pos_y+j
                        # ensure in bounds
                        if cx >= 0 and cx < game_width and cy >= 0 and cy < game_height:
                            check_tile(cx, cy)
                            if game_context["dead"]:
                                break
                    if game_context["dead"]:
                        break
                
            elif command.startswith("f") and not first_click:
                is_flag = current_tile == TILE_FLAG
                is_unkn = current_tile == TILE_UNKNOWN
                tiles[current_tile_index] = TILE_FLAG if is_unkn else TILE_UNKNOWN if is_flag else current_tile
                flags_taken = -1 if is_unkn else 1 if is_flag else 0
                game_context["flag_count"] = game_context["flag_count"] + flags_taken

            # after it finishes, we need to check for a few things
            all_mines_found = __check_if_mines_are_lonely(tiles, mines, pos_x, pos_y, game_width, game_height, current_tile_index)
            if all_mines_found:
                # the player won
                game_context["dead"] = True
                running = False
                __win()
                return

            # make game dirty if not won
            game_context["dirty"] = True

    def __win():
        procedures_list = [
            procedures.defproc(1, "Submit to Leaderboard", __save_to_leaderboard),
            procedures.defproc(0, "Exit", None)
        ]

        after_header = str(ansi.fgcolor(ansi.bold("Congratulations! You took {:.2f} seconds to finish the game!".format(game_context["time"])),
                                        terminal.COLOR_YELLOW))

        before_header = None

        submitted_to_leaderboard = False
        while True:
            _, option, _ = procedures.ask_procedure((ansi.fgcolor(ansi.bold("CONGRATULATIONS!!"), terminal.COLOR_YELLOW)) if terminal.use_advanced_terminal_graphics else "CONGRATULATIONS!!",
                                                    "+",
                                                    procedures_list,
                                                    status_footer=before_header,
                                                    after_header=after_header if terminal.use_advanced_terminal_graphics else ansi.get_raw_string(after_header))

            if option == 1:
                if submitted_to_leaderboard:
                    before_header = "Already submitted."
                    continue
                else:
                    submitted_to_leaderboard = True
                    before_header = "Submitted!"

            status_code = procedures.do_execute_procedure(procedures_list, option)
            if status_code != STATUS_SUCCESS:
                before_header = "Invalid option."
                continue

            if option == 0:
                break # exit

    def __serialize_board(board):
        def __special2letter(given):
            if given == TILE_MINE:
                return "M"
            elif given == TILE_FLAG:
                return "F"
            elif given == TILE_CLEAR:
                return " "
            elif given == TILE_UNKNOWN:
                return "?"
            return str(given)
        
        serialized = ""
        for ch in board:
            serialized += __special2letter(ch)
        return serialized

    def __serialize_mines(mines):
        serialized = ""
        for x, y in mines:
            serialized += __to_coordinate_numbers(x)
            serialized += __to_coordinate_numbers(y)
        return serialized

    def __deserialize_mines(serialized):
        mines = []
        xbuf = None
        for ch in serialized:    
            if xbuf is not None:
                ybuf = __to_real_numbers(ch)
                if ybuf is None:
                    return STATUS_UNDERPOPULATED, None
                mines.append((xbuf, ybuf))
                xbuf = None
            else:
                xbuf = __to_real_numbers(ch)
                if xbuf is None:
                    return STATUS_UNDERPOPULATED, None

        return STATUS_SUCCESS, mines

    def __deserialize_board(serialized):
        def __letter2special(given):
            if given == "M":
                return TILE_MINE
            elif given == "F":
                return TILE_FLAG
            elif given == " ":
                return TILE_CLEAR
            elif given == "?":
                return TILE_UNKNOWN
            return safeint(given)
        
        board = []
        for ch in serialized:    
            tile = __letter2special(ch)
            if tile is None:
                return STATUS_BAD_USER_INPUT, None
            board.append(tile)

        return STATUS_SUCCESS, board

    def __save_to_leaderboard():
        name = dialog.input("What is your name?")
        assert name is not None
        name = name.replace(",", "")

        new_entry = f"{name},{game_context["time"]},{game_context["width"]},{game_context["height"]},{len(game_context["mines"])},{__serialize_board(game_context["board"])}"

        status_code, leaderboard = persistence.load_persistence("leaderboard-minesweeper")
        if status_code == STATUS_SUCCESS and leaderboard is not None:
            nextEntry = safeint(leaderboard.get("NextEntry", "1")) or 1
            nextEntry += 1

            leaderboard["NextEntry"] = str(nextEntry)
            leaderboard[f"Entry{nextEntry}"] = new_entry
        else:
            leaderboard = {}
            leaderboard["NextEntry"] = 1
            leaderboard[f"Entry{leaderboard["NextEntry"]}"] = new_entry

        persistence.save_persistence("leaderboard-minesweeper", leaderboard)

        __view_leaderboard()

    def __view_leaderboard():
        status_code, leaderboard = persistence.load_persistence("leaderboard-minesweeper")
        if status_code == STATUS_FILE_NOT_FOUND:
            print_error("Leaderbord has not been created yet. Play a game first then submit a run to the leaderboard!")
            return

        if status_code != STATUS_SUCCESS or leaderboard is None:
            print_error("Leaderboard cannot be loaded because of file corruption.")
            return

        # first step in loading the leaderboard, get the number of entries
        entry_count = safeint(leaderboard.get("NextEntry", "1")) or 1

        # second step is iterate and parse through entries
        real_leaderboard = []
        for i in range(entry_count+1):
            entry = leaderboard.get(f"Entry{i+1}")
            if entry is None:
                continue

            parsed_entry = entry.split(",")
            if len(parsed_entry) != 6: # terminate immediately
                continue
            name, time, width, height, mines_count, board = parsed_entry[0], parsed_entry[1], parsed_entry[2], parsed_entry[3], parsed_entry[4], parsed_entry[5]
            status_code, actual_board = __deserialize_board(board)
            if actual_board is None or status_code is not STATUS_SUCCESS:
                continue

            real_leaderboard.append((name, safefloat(time), safeint(width), safeint(height), safeint(mines_count), actual_board))

        # sort them as well
        def leaderboard_comparator(this, that):
            return this[1] - that[1]
        sort(real_leaderboard, leaderboard_comparator)

        # third is make it all procedures
        procedure_list = [
            procedures.defproc(0, "Exit", None)
        ]
        for i in range(len(real_leaderboard)):
            entry = real_leaderboard[i]
            procedure_list.append(procedures.defproc(i + 1, f"{entry[0]}, {entry[1] if entry[1] is not None else "Unknown":.2f} secs, "\
                                                     f"{entry[2] if entry[2] is not None else "?"}x{entry[3] if entry[3] is not None else "?"}, "\
                                                    f"{entry[4] if entry[4] is not None else "?"} mines", 
                                                    lambda entry=entry: __view_dead_board(entry[0], entry[5], entry[1], entry[2], entry[3])))

        status_footer = None
        procedure_offset = 0
        while True:
            status_code, option_or_page, _ = procedures.ask_procedure("Leaderboard",
                                                    "v",
                                                    procedure_list,
                                                    status_footer=status_footer,
                                                    procedure_offset=procedure_offset,
                                                    procedure_limit=10)

            if status_code == STATUS_SUCCESS and option_or_page == 0:
                break # exit

            if status_code == STATUS_NEXT and option_or_page:
                procedure_offset += option_or_page
                continue
            elif status_code == STATUS_PREVIOUS and option_or_page:
                procedure_offset -= option_or_page
                continue

            status_code = procedures.do_execute_procedure(procedure_list, option_or_page)
            
            if status_code != STATUS_SUCCESS:
                status_footer = "Invalid option."
                continue

    def __view_dead_board(name, board, time, width, height):
        nonlocal game_context, running
        old_game_context = game_context.copy()
        game_context["dead"] = True
        game_context["board"] = board
        game_context["flag_count"] = 0
        game_context["mines"] = []
        game_context["time"] = time
        game_context["width"] = width
        game_context["height"] = height

        running = True
        while running:
            __draw_grid()
            __user_input()

        game_context = old_game_context


    def __check_if_mines_are_lonely(tiles, mines, x, y, w, h, idx):
        unrevealed = 0
        for tile_value in tiles:
            if tile_value == TILE_UNKNOWN or tile_value == TILE_FLAG:
                unrevealed += 1
        return unrevealed == len(mines)

    def __find_not_mines_algorithm(tiles, mines, x, y, w, h, idx):
        # okay we know tiles[idx] is not a mine
        # we then need to find its neighboards and let it think
        checked = [] # add memo to prevent checking already checked
        neighbors = []
        next_neighbors_queue = [(x, y)]
        while True:
            if len(next_neighbors_queue) == 0:
                break

            current_neighbor = next_neighbors_queue.pop(0)
            if find(checked, current_neighbor) is not None:
                continue

            nx, ny = current_neighbor[0], current_neighbor[1]
            if (nx < 0 or nx > w - 1) or (ny < 0 or ny > h - 1): # if neighbor oob then just dont
                continue

            # in order to "queue" that neighbor, it must satisfy some conditions:
            # 1) there must be no mine at that neighbor
            # 2) there must be no adjacnet mine at that neighbor
            if find(mines, (nx, ny)) is not None: # condition 1
                continue

            # ther emust be no adjacent mine at that neighbot
            # but how do we check for adjacemnt mine in the first place?
            adjacent_mine_count = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    nax, nay = nx+i, ny+j
                    # ensure in bounds
                    if nax >= 0 and nax < w and nay >= 0 and nay < h:
                        if find(mines, (nax, nay)) is not None:
                            adjacent_mine_count += 1

            # if we clicked on a tile that has an adjacent mine on it, then skip the algorithm entirely
            if nx == x and ny == y and adjacent_mine_count > 0:
                tiles[idx] = adjacent_mine_count
                break

            # if there are no counted adjacent mines
            # then we can add it to the queued neighbors

            n_idx = ny * w + nx
            if adjacent_mine_count > 0:
                tiles[n_idx] = adjacent_mine_count
                continue
            else:
                tiles[n_idx] = TILE_CLEAR

            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0:
                        continue
                    next_neighbors_queue.append((nx + i, ny + j))
            neighbors.append((nx, ny))
            checked.append((nx, ny))

    # i would do the no-guess algorithm if i have time
    # but deadline is near so i'd rather do random generation        
    def __generate_mines(mines, width, height, number_of_mines, excluded_positions):
        for _ in range(number_of_mines):
            while True:
                mx, my = random.randint(0, width-1), random.randint(0, height-1)
                if find(excluded_positions, (mx, my)) is not None or find(mines, (mx, my)) is not None:
                    continue
                mines.append((mx, my))
                break
        
    def destroy():
        pass

    return {
        "init": init,
        "run": run,
        "destroy": destroy
    }
    