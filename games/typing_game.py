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
                            f"Please verify directory structure and that the word bank file exists.")

        return success


    def run(self):
        procedures_list = [
            procedures.defproc(1, "Start", self.game),
            procedures.defproc(2, "Leaderboards", None),
            procedures.defproc(3, "Settings", None),
            procedures.defproc(0, "Exit", None)
        ]

        before_header = None
        while True:
            status_code, option = procedures.print_ask_execute_procedures("Typing Game!!", "+",
                                                                          procedures_list,
                                                                          before_header=before_header,
                                                                          after_header=RULES)
            if status_code != STATUS_SUCCESS:
                before_header = "Invalid option."
                continue
            else:
                before_header = None

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

    def __judge(self, correct_input_list, user_input_list):
        if len(correct_input_list) < len(user_input_list):
            return STATUS_UNDERPOPULATED, 0, []

        judgement_table = []
        score = 0
        for i in range(len(correct_input_list)):
            correct_input = correct_input_list[i]
            user_input = user_input_list[i]
            letter_count = len(correct_input)
            if not letter_count in self.score_per_letter_count:
                print_error(f"Score per {letter_count}-letter word is missing right now... How come?")
                return STATUS_UNDERPOPULATED, 0, []
            given_score = self.score_per_letter_count[letter_count]
            if correct_input == user_input:
                score += given_score
            judgement_table = (correct_input, user_input, given_score if correct_input == user_input else 0)

        return STATUS_SUCCESS, score

    def __print_countdown(self):
        max_width = max(terminal.get_string_visual_width("The typing game starts in..."),
                        terminal.get_string_visual_width("3... 2... 1... GO!!!!"))
        width = terminal.get_width()
        height = terminal.get_height()
        pos_x = width / 2 - max_width / 2
        pos_y = height / 2
        countdown = ""

        if not terminal.use_advanced_terminal_graphics:
            print("The typing game starts in...")

        for i in range(4, 0, -1):
            if i == 1:
                countdown += str(terminal.ansify("GO!!!!").bold()) \
                    if terminal.use_advanced_terminal_graphics else "GO!!!!"
            elif (i - 1) < 4:
                countdown += str(terminal.ansify(f"{i - 1}... ").bold().fgcol(terminal.COLOR_RED if i == 3 else
                                                                              terminal.COLOR_YELLOW if i == 2 else
                                                                              terminal.COLOR_GREEN)) \
                    if terminal.use_advanced_terminal_graphics else f"{i - 1}... "
            if terminal.use_advanced_terminal_graphics:
                terminal.erase_whole_screen()
                terminal.tgfx_print_text("=============================", pos_x, pos_y - 1)
                terminal.tgfx_print_text("The typing game starts in...", pos_x, pos_y)
                terminal.tgfx_print_text(countdown, pos_x, pos_y + 1)
                terminal.tgfx_print_text("> ", pos_x, pos_y + 3)
                terminal.tgfx_print_text("=============================", pos_x, pos_y + 4)
                terminal.put_cursor_to(pos_x + 3, height / 2 + 3)
                terminal.flush()
            else:
                print(countdown)
            time.sleep(0.5)

    def __print_word(self, word):
        if terminal.use_advanced_terminal_graphics:
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
            print(terminal.ansify().bold().persist(), end="")
            terminal.tgfx_print_text(word, pos_x, pos_y + 1)
            print(terminal.ESCAPE_RESET_GRAPHICS, end="")
            terminal.tgfx_print_text("> ", pos_x, pos_y + 3)
            terminal.tgfx_print_text("======================================", pos_x, pos_y + 4)
            terminal.put_cursor_to(pos_x + 3, height / 2 + 3)
        else:
            print("TYPE THE WORD BELOW THEN PRESS [Enter]")
            print(word)
            print("> ", end="")

    def __print_congrats(self, time_taken, score, judgement_table):
        if terminal.use_advanced_terminal_graphics:
            print(terminal.ansify("Congratulations! You took {:.2f} seconds to type all words.".format(time_taken))
                  .bold().fgcol(terminal.COLOR_YELLOW))
            print(terminal.ansify("Your score is {:d}. Nice!!".format(score))
                  .bold().fgcol(terminal.COLOR_YELLOW))
        pass

    def game(self):
        status_code = self.__validate_invariants()

        if status_code != STATUS_SUCCESS:
            print_error(f"The game could not be started: {STATUS_CODE_TO_LITERAL_TABLE[status_code]}")
            return

        status_code, words = self.__build_word_sequence()

        if status_code != STATUS_SUCCESS:
            print_error(f"The game could not be started: {STATUS_CODE_TO_LITERAL_TABLE[status_code]}")
            return

        self.__print_countdown()

        timestamp_start = time.time()
        user_typed_words = []
        for word in words:
            self.__print_word(word)

            user_input = input()
            user_typed_words.append(user_input)

        terminal.erase_whole_screen()
        terminal.reset_cursor_to_top_left()

        time_taken = time.time() - timestamp_start
        status_code, score, judgement_table = self.__judge(words, user_typed_words)
        if status_code == STATUS_SUCCESS:
            self.__print_congrats(time_taken, score, judgement_table)
        else:
            print_error(f"The score could not be calculated: {status_code}")


    def destroy(self):
        pass