from common import print_error
from data import word_bank
from games.base_game import BaseGame

import procedures

import time

class TypingGame(BaseGame):
    def init(self):
        error_code, word_count = word_bank.try_loading_words()
        success = (error_code == word_bank.ERROR_SUCCESS
                   or error_code == word_bank.ERROR_LOADED)

        if not success:
            if error_code == word_bank.ERROR_FILE_NOT_FOUND:
                print_error("Word bank not found. "
                            "Please verify directory structure and that ./data/words_alpha.txt exists.")

        return success


    def run(self):
        procedures_list = [
            procedures.defproc(1, "Start", self.run),
            procedures.defproc(2, "Leaderboards", None),
            procedures.defproc(0, "Exit", None)
        ]

        while True:
            procedures.print_procedures("Typing Game!!", "+", procedures_list)
            success, option = procedures.ask_and_execute_procedure(procedures_list)
            if not success:
                print("Invalid option")
                continue

            if option == 0:  # exit option
                break

    def game(self):
        return 0

    def destroy(self):
        pass