from common import *

def __about():
    print("\x1b[36mHi\x1b[0m")

def __leaderboard_comparator(this, that):
    return this["ranking"] - that["ranking"]

def __show_leaderboard(players):
    sort(players, __leaderboard_comparator)

    page_offset = 0
    page_count = len(players)
    max_page_view = 10
    message = ""

    while True:
        print("\x1b[30;47m ^^^ Leaderboard ^^^\x1b[0m")

        page_end = min(page_count, page_offset + max_page_view)

        for index in range(page_offset, page_end):
            if index == 0: # first
                color_code = "\x1b[93;1m"
            elif index == 1: # second
                color_code = "\x1b[1;38;5;249m"
            elif index == 2: # third
                color_code = "\x1b[1;38;5;130m"
            else:
                color_code = "\x1b[1m"
            
            player = players[index]
            name = player.get("name", "Anonymous")
            score = player.get("score", 0)

            print(f"{color_code} - [{index - page_offset + 1}]: {name}; {score} pts.\x1b[0m")

        show_prev = page_offset > 0
        show_next = page_end < page_count

        print()
        if show_prev:
            print("\x1b[1m - [Q]: Previous\x1b[0m")
        if show_next:
            print("\x1b[1m - [W]: Next\x1b[0m")
        print("\x1b[1m - [0]: Exit\x1b[0m")
        print(f"\x1b[36m{message!s}\x1b[0m")
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

def __print_equation(equation, name, is_bot, lives, time_left, message):
    s0 = f"Player \x1b[2m{name} {'(Bot)' if is_bot else ''}\x1b[22m; \x1b[33m({lives}/3)\x1b[37m lives; \x1b[33m{time_left:.2f}\x1b[37m s left!"
    s1 = "SOLVE THE FOLLOWING EQUATION! QUICKLY!!"
    s2 = equation + " = ???"
    print()
    print("\x1b[37;2m----------------\x1b[0m")
    print(f"\x1b[37m{s0}\x1b[0m")
    print("\x1b[37;2m----------------\x1b[0m")
    print(f"\x1b[31;1m{s1}\x1b[0m")
    print(f"\x1b[37;1m{s2}\x1b[0m")
    if message:
        print(f"\x1b[33m{'[!] ' + message}\x1b[0m")
    print(f"\x1b[32m> {('Bot is thinking...' if is_bot else '')}\x1b[0m", end="", flush=True)
