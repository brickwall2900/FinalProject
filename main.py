import os
import random
import time

import games.typing_game

import common
from procedures import defproc, print_procedures, ask_and_execute_procedure


def init():
    pass

def loop():
    procedures = [
        defproc(1, "Hello", init),
        defproc(0, "Exit", None)
    ]

    while True:
        print_procedures("Medicine Inventory System", "#", procedures)
        success, option = ask_and_execute_procedure(procedures)
        if not success:
            print("Invalid option")
            continue

        if option == 0: # exit option
            break

def destroy():
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