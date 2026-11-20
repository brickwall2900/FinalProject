import persistence

import time
import random

from common import safeint, print_error, sort
from games.minesweeper.saveload import __serialize_board, __serialize_mines
from games.minesweeper.ui import __view_dead_board

def __save_to_leaderboard(game_context):
    name = input("What is your name? ")

    leaderboard = persistence.load_persistence("leaderboard-minesweeper")
    current_entry = 0

    if leaderboard is not None:
        current_entry = safeint(leaderboard.get("CurrentEntry"), 0)
        current_entry += 1

        leaderboard["CurrentEntry"] = str(current_entry)
    else:
        leaderboard = {}
        leaderboard["CurrentEntry"] = "0"

    leaderboard[f"Entry{current_entry}"] = name
    leaderboard[f"Entry{current_entry}_time_taken"] = str(int(game_context["time"] * 100))
    leaderboard[f"Entry{current_entry}_width"] = str(game_context["width"])
    leaderboard[f"Entry{current_entry}_height"] = str(game_context["height"])
    leaderboard[f"Entry{current_entry}_mines"] = __serialize_mines(game_context["mines"])
    leaderboard[f"Entry{current_entry}_mine_count"] = len(game_context["mines"])
    leaderboard[f"Entry{current_entry}_board"] = __serialize_board(game_context["board"])

    persistence.save_persistence("leaderboard-minesweeper", leaderboard)

    __view_leaderboard(game_context)

def __leaderboard_comparator(this, that):
    return this[1] - that[1]

def __parse_leaderboard(loaded_leaderboard):
    the_leaderboard = []

    entry_count = safeint(loaded_leaderboard.get("CurrentEntry"), 0)

    for i in range(entry_count + 1):
        entry_key = f"Entry{i}"

        name = loaded_leaderboard.get(entry_key)
        if name is None:
            continue

        time = safeint(loaded_leaderboard.get(entry_key + "_time_taken"))
        width = safeint(loaded_leaderboard.get(entry_key + "_width"))
        height = safeint(loaded_leaderboard.get(entry_key + "_height"))
        mines = loaded_leaderboard.get(entry_key + "_mines")
        mine_count = safeint(loaded_leaderboard.get(entry_key + "_mine_count"))
        board = loaded_leaderboard.get(entry_key + "_board")

        if time is None \
            or width is None \
            or height is None \
            or mines is None \
            or mine_count is None \
            or board is None:
            continue

        time = time / 100 # compensate float to int by division by 100

        the_leaderboard.append((name, time, width, height, mine_count, mines, board))

    return the_leaderboard

def __view_leaderboard(game_context):
    loaded_leaderboard = persistence.load_persistence("leaderboard-minesweeper")

    if loaded_leaderboard is None:
        print_error("Leaderboard cannot be loaded because you haven't played a game yet, or because of file corruption.")
        return

    the_leaderboard = __parse_leaderboard(loaded_leaderboard)

    sort(the_leaderboard, __leaderboard_comparator)

    __paginate_and_navigate_leaderboard(game_context, the_leaderboard)

def __paginate_and_navigate_leaderboard(game_context, leaderboard):
    page_offset = 0
    page_count = len(leaderboard)
    max_page_view = 10
    message = ""

    while True:
        print(" ^^^ Leaderboard ^^^")

        page_end = min(page_count, page_offset + max_page_view)
        items_on_page = page_end - page_offset

        for index in range(page_offset, page_end):
            entry = leaderboard[index]
            name = entry[0]
            time = entry[1]
            width = entry[2]
            height = entry[3]
            mine_count = entry[4]

            print(f" - [{(index - page_offset) + 1}]: {name}; {time} seconds; {width}x{height} w/ {mine_count} mines.")

        show_prev = page_offset > 0
        show_next = page_end < page_count

        print()
        if show_prev:
            print(" - [Q]: Previous")
        if show_next:
            print(" - [W]: Next")
        print(" - [0]: Exit")
        print(message)
        raw_chosen = input("> ").lower().strip()
        chosen = safeint(raw_chosen)
        message = ""

        if chosen is None:
            if raw_chosen.startswith("q") and page_offset - max_page_view >= 0:
                page_offset = page_offset - max_page_view
            elif raw_chosen.startswith("w") and page_offset + max_page_view < page_count - 1:
                page_offset = page_offset + max_page_view
            else:
                message = "Invalid option, try again."
            continue

        if chosen == 0:
            break
        else:
            if not (1 <= chosen <= items_on_page):
                message = "Invalid option, try again."
                continue
            real_index = page_offset + (chosen - 1)
            leaderboard_entry = leaderboard[real_index]
            time = leaderboard_entry[1]
            width = leaderboard_entry[2]
            height = leaderboard_entry[3]
            __view_dead_board(game_context, leaderboard_entry[5], leaderboard_entry[6], time, width, height)
