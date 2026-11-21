import time

from common import safeint, pause
from games.typing_game.leaderboards import view_score_table, save_to_leaderboard

def view_about():
    print("The Typing Game tests how fast you can type words correctly!!" \
    " Type more words correctly, the more points you get. Better if you can type" \
    " words with speed and accuracy!")
    pause()

    print("TLDR; Type correct words = more points")
    print("The below example will mark your input as CORRECT")
    print()
    print("test")
    print()
    print("> test (<- this is your input box)")
    
    pause()

    print("The below example will mark your input as INCORRECT; you get 0 points.")
    print()
    print("hello")
    print()
    print("> henlo")

    pause()

def print_countdown():
    countdown = ""

    print("The typing game starts in...")

    for i in range(4, 0, -1):
        if i == 1:
            countdown += "GOO!!!!"
        elif (i - 1) < 4:
            countdown += f"{i - 1}... "

        print(countdown)
        time.sleep(0.5)

def print_word(word, future_words, settings):
    # get the 5 first future words
    future_words_printed = " ".join([future_words[i] for i in range(len(future_words)) if i < 5]) if settings["show_words_in_advance"] else ""

    print("TYPE THE HIGHLIGHTED WORD BELOW THEN PRESS [Enter]")
    print(f">> {word} << {future_words_printed}")
    print("> ", end="")

def print_congrats(time_taken, score, words_per_minute, judgement_table):
    submitted = False
    message = ""
    while True:
        print("~~~^ CONGRATULATIONS ^~~~")
        print(f"Congratulations! You took {time_taken:.2f} seconds ({words_per_minute} WPM) to type all words.")
        print()
        print(f"Your score is {score}. Good job!")

        print(" - [1] View Score Table")
        print(" - [2] Submit to Leaderboard")
        print()
        print(" - [0]: Exit")
        print(message)

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
