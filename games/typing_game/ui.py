import time

from common import safeint, pause
from games.typing_game.leaderboards import view_score_table, save_to_leaderboard

def view_about():
    print("\x1b[37mThe Typing Game tests how fast you can type words correctly!! Type more words correctly, the more points you get. Better if you can type words with speed and accuracy!\x1b[0m")
    pause()

    print("\x1b[37mTLDR; Type correct words = more points\x1b[0m")
    print("\x1b[37mThe below example will mark your input as \x1b[32;1mCORRECT\x1b[0m")
    print()
    print("\x1b[1mtest\x1b[0m")
    print()
    print(">\x1b[4m test\x1b[0m (<- this is your input box)\x1b[0m")
    
    pause()

    print("\x1b[37mThe below example will mark your input as \x1b[91;1mINCORRECT\x1b[0;37m; you get 0 points.\x1b[0m")
    print()
    print("\x1b[1mhello\x1b[0m")
    print()
    print(">\x1b[4m henlo\x1b[0m")

    pause()

def print_countdown():
    countdown = ""

    print("\x1b[30;47mThe typing game starts in...\x1b[0m")

    for i in range(4, 0, -1):
        if i == 1:
            countdown += "\x1b[32;1mGOO!!!!"
        elif (i - 1) < 4:
            countdown += f"\x1b[{91 if i == 4 else 33 if i == 3 else 32};22m{i - 1}... "

        print(f"{countdown}\x1b[0m")
        time.sleep(0.5)

def print_word(word, future_words, settings):
    # get the 5 first future words
    future_words_printed = " ".join([future_words[i] for i in range(len(future_words)) if i < 5]) if settings["show_words_in_advance"] else ""

    print("\x1b[30;47m === TYPE THE HIGHLIGHTED WORD BELOW THEN PRESS [Enter] === \x1b[0m")
    print(f"\x1b[1m>> {word} << \x1b[22m{future_words_printed}\x1b[0m")
    print("> \x1b[4m", end="")

def print_congrats(time_taken, score, words_per_minute, judgement_table):
    submitted = False
    message = ""
    while True:
        print("\x1b[30;43m ~~~^ CONGRATULATIONS ^~~~ \x1b[0m")
        print(f"\x1b[37mCongratulations! You took \x1b[33m{time_taken:.2f}\x1b[37m seconds \x1b[2m({words_per_minute} WPM)\x1b[22m to type all words.\x1b[0m")
        print()
        print(f"\x1b[37mYour score is \x1b[32m{score}\x1b[37m. Good job!\x1b[0m")

        print("\x1b[1m - [1] View Score Table\x1b[0m")
        print("\x1b[1m - [2] Submit to Leaderboard\x1b[0m")
        print()
        print("\x1b[1m - [0]: Exit\x1b[0m")
        print(f"\x1b[33m{message}\x1b[0m")

        chosen = safeint(input("> "))
        message = ""
        if chosen is None:
            message = "Invalid option, try again."
            continue

        if chosen == 1:
            view_score_table(judgement_table)
        elif chosen == 2 and not submitted:
            save_to_leaderboard(time_taken, score, words_per_minute, judgement_table)
            submitted = True
        elif chosen == 0:
            break
        else:
            message = "Invalid option, try again."
