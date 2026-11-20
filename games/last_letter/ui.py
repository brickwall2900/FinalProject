from common import *

def __about():
    print("Word Bomb ")

def __leaderboard_comparator(this, that):
    return this["ranking"] - that["ranking"]

def __show_leaderboard(players):
    sort(players, __leaderboard_comparator)

    page_offset = 0
    page_count = len(players)
    max_page_view = 10
    message = ""

    while True:
        print(" ^^^ Leaderboard ^^^")

        page_end = min(page_count, page_offset + max_page_view)
        items_on_page = page_end - page_offset

        for index in range(page_offset, page_end):
            player = players[index]
            name = player.get("name", "Anonymous")
            score = player.get("score", 0)

            print(f" - [{(index - page_offset) + 1}]: {name}; {score} pts.")

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
            if raw_chosen.startswith("q") and show_prev:
                page_offset = page_offset - max_page_view
            elif raw_chosen.startswith("w") and show_next:
                page_offset = page_offset + max_page_view
            else:
                message = "Invalid option, try again."
            continue

        if chosen == 0:
            break

def __print_letter(start_or_end, letters, name, is_bot, lives, time_left, max_time_left, message):
    LETTER_START        = 0
    LETTER_END          = 1
    
    fuse_length = "~" * int((time_left / max_time_left) * 4)
    
    s0 = f"Player {name} {'(Bot)' if is_bot else ''}; ({lives}/3) lives;"
    s1 = f"(^){fuse_length} ({time_left:.2f} s) TYPE THE WORD {'STARTING' if start_or_end == LETTER_START else 'ENDING'} WITH"
    
    underscores = ("_" * clamp(10 - len(letters), 0, 10))
    s2 = (letters + underscores) if start_or_end == LETTER_START else (underscores + letters)
    
    print("----------------")
    print(s0)
    print(s1)
    print(s2)
    if message:
        print("[!] " + message)
    print(f"> {'Bot is thinking...' if is_bot else ''}", end="", flush=True)
