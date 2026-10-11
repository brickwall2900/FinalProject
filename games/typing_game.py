import os

import terminal
from common import print_error, shuffle
from data import word_bank
from games.base_game import BaseGame

import procedures

import time
import random

from status import STATUS_UNDERPOPULATED, STATUS_SUCCESS, STATUS_ALREADY_EXISTS, STATUS_FILE_NOT_FOUND, \
    STATUS_CODE_TO_LITERAL_TABLE

RULES = "The Typing Game tests your typing skills by you typing words with speed and accuracy!"

class TypingGame(BaseGame):
    words_in_random = True
    letter_count_to_include = [3, 4, 5]
    word_count_per_letter_count = { 3: 7, 4: 7, 5: 7 }
    score_per_letter_count = { 3: 2, 4: 5, 5: 7 }

    def init(self):
        error_code, word_count = word_bank.try_loading_words()
        success = (error_code == STATUS_SUCCESS
                   or error_code == STATUS_ALREADY_EXISTS)

        if not success:
            if error_code == STATUS_FILE_NOT_FOUND:
                print_error("Word bank not found. "
                            "Please verify directory structure and that ./data/words_alpha.txt exists.")

        return success


    def run(self):
        procedures_list = [
            procedures.defproc(1, "Start", self.game),
            procedures.defproc(2, "Leaderboards", None),
            procedures.defproc(3, "Settings", None),
            procedures.defproc(0, "Exit", None)
        ]

        while True:
            procedures.print_procedures("Typing Game!!", "+", procedures_list,
                                        after_header=RULES)
            success, option = procedures.ask_and_execute_procedure(procedures_list)
            if not success:
                print("Invalid option")
                continue

            if option == 0:  # exit option
                break

    # picks random words with a criteria, that `count`
    # words will be given with `letter_count` letters in it from the word bank.
    def __pick_words(self, count, letter_count):
        letter_count_words = [word for word in word_bank.words if len(word) == letter_count]

        if len(letter_count_words) < count:
            return STATUS_UNDERPOPULATED, None

        shuffle(letter_count_words)

        return STATUS_SUCCESS, letter_count_words[:count]

    def __build_word_sequence(self):
        result = []

        for letter_count in self.letter_count_to_include:
            status_code, words = self.__pick_words(self.word_count_per_letter_count[letter_count], letter_count)
            if status_code == STATUS_SUCCESS:
                result.extend(words)
            else:
                assert status_code == STATUS_UNDERPOPULATED
                print_error(f"Insufficient words in word bank. Please provide more {letter_count}-letter words.")
                return status_code, None

        if self.words_in_random:
            shuffle(result)

        return STATUS_SUCCESS, result

    def __validate_invariants(self):
        if len(self.letter_count_to_include) <= 0:
            print_error("At least one n-letter count must be specified.")
            return STATUS_UNDERPOPULATED

        for letter_count in self.letter_count_to_include:
            if not letter_count in self.word_count_per_letter_count:
                print_error(f"The word count for {letter_count}-letter words is unspecified.")
                return STATUS_UNDERPOPULATED

            if not letter_count in self.score_per_letter_count:
                print_error(f"The score for {letter_count}-letter words is unspecified.")
                return STATUS_UNDERPOPULATED

        return STATUS_SUCCESS

    def game(self):
        status_code = self.__validate_invariants()

        if status_code != STATUS_SUCCESS:
            print_error(f"The game could not be started: {STATUS_CODE_TO_LITERAL_TABLE[status_code]}")
            return

        status_code, words = self.__build_word_sequence()

        if status_code != STATUS_SUCCESS:
            print_error(f"The game could not be started: {STATUS_CODE_TO_LITERAL_TABLE[status_code]}")
            return

        print("The typing game starts in...")
        time.sleep(0.5)
        for i in range(3, 0, -1):
            print(i)
            time.sleep(0.5)

        print("GOO!!")

        timestamp_start = time.time()
        user_typed_words = []
        for word in words:
            terminal.erase_whole_screen()
            terminal.reset_cursor_to_top_left()
            max_width = max(terminal.get_string_visual_width("TYPE THE WORD BELOW THEN PRESS [Enter]"),
                            terminal.get_string_visual_width(word))

            width = terminal.get_width()
            height = terminal.get_height()
            pos_x = width / 2 - max_width / 2
            pos_y = height / 2

            terminal.tgfx_print_text("======================================", pos_x, pos_y - 1)
            terminal.tgfx_print_text("TYPE THE WORD BELOW THEN PRESS [Enter]", pos_x, pos_y)
            terminal.tgfx_print_text(word, pos_x, pos_y + 1)
            terminal.tgfx_print_text("> ", pos_x, pos_y + 3)
            terminal.tgfx_print_text("======================================", pos_x, pos_y + 4)
            terminal.put_cursor_to(pos_x + 3, height / 2 + 3)

            user_input = input()
            user_typed_words.append(user_input)

        terminal.erase_whole_screen()
        terminal.reset_cursor_to_top_left()

        time_taken = time.time() - timestamp_start
        print(terminal.ansify("Congratulations! You took {:.2f} seconds to type all words.".format(time_taken)).bold().fgcol(terminal.COLOR_YELLOW))


    def destroy(self):
        pass