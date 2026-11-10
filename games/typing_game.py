import os

import ansi
import terminal
from common import print_error, shuffle
from data import word_bank

import procedures

import time
import random

from status import STATUS_UNDERPOPULATED, STATUS_SUCCESS, STATUS_ALREADY_EXISTS, STATUS_FILE_NOT_FOUND, \
    STATUS_CODE_TO_LITERAL_TABLE

RULES = "The Typing Game tests your typing skills by you typing words with speed and accuracy!"

def typing_game():
    words_in_random = True
    letter_count_to_include = [3, 4, 5]
    word_count_per_letter_count = { 3: 7, 4: 7, 5: 7 }
    score_per_letter_count = { 3: 2, 4: 5, 5: 7 }

    def init():
        error_code, word_count = word_bank.try_loading_words()
        success = (error_code == STATUS_SUCCESS
                   or error_code == STATUS_ALREADY_EXISTS)

        if not success:
            if error_code == STATUS_FILE_NOT_FOUND:
                print_error("Word bank not found. "
                            f"Please verify directory structure and that the word bank file exists.")

        return success

    def run():
        procedures_list = [
            procedures.defproc(1, "Start", game),
            procedures.defproc(2, "Leaderboards", None),
            procedures.defproc(3, "Settings", None),
            procedures.defproc(0, "Exit", None)
        ]

        before_header = None
        while True:
            status_code, option = procedures.print_ask_execute_procedures("Typing Game!!", "+",
                                                                          procedures_list,
                                                                          status_footer=before_header,
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
    def __pick_words(count, letter_count):
        letter_count_words = [word for word in word_bank.words if len(word) == letter_count]

        if len(letter_count_words) < count:
            return STATUS_UNDERPOPULATED, None

        shuffle(letter_count_words)

        return STATUS_SUCCESS, letter_count_words[:count]

    def __build_word_sequence():
        result = []

        for letter_count in letter_count_to_include:
            status_code, words = __pick_words(word_count_per_letter_count[letter_count], letter_count)
            if status_code == STATUS_SUCCESS:
                result.extend(words)
            else:
                assert status_code == STATUS_UNDERPOPULATED
                print_error(f"Insufficient words in word bank. Please provide more {letter_count}-letter words.")
                return status_code, None

        if words_in_random:
            shuffle(result)

        return STATUS_SUCCESS, result

    def __validate_invariants():
        if len(letter_count_to_include) <= 0:
            print_error("At least one n-letter count must be specified.")
            return STATUS_UNDERPOPULATED

        for letter_count in letter_count_to_include:
            if not letter_count in word_count_per_letter_count:
                print_error(f"The word count for {letter_count}-letter words is unspecified.")
                return STATUS_UNDERPOPULATED

            if not letter_count in score_per_letter_count:
                print_error(f"The score for {letter_count}-letter words is unspecified.")
                return STATUS_UNDERPOPULATED

        return STATUS_SUCCESS

    def __judge(correct_input_list, user_input_list):
        if len(correct_input_list) < len(user_input_list):
            return STATUS_UNDERPOPULATED, 0, []

        judgement_table = []
        score = 0
        for i in range(len(correct_input_list)):
            correct_input = correct_input_list[i]
            user_input = user_input_list[i]
            letter_count = len(correct_input)
            if not letter_count in score_per_letter_count:
                print_error(f"Score per {letter_count}-letter word is missing right now... How come?")
                return STATUS_UNDERPOPULATED, 0, []
            given_score = score_per_letter_count[letter_count]
            if correct_input == user_input:
                score += given_score
            judgement_table.append((correct_input, user_input, given_score if correct_input == user_input else 0))

        return STATUS_SUCCESS, score, judgement_table

    def __print_countdown():
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
                countdown += str(ansi.bold("GO!!!!")) \
                    if terminal.use_advanced_terminal_graphics else "GO!!!!"
            elif (i - 1) < 4:
                countdown += str(ansi.fgcolor(ansi.bold(f"{i - 1}... "), terminal.COLOR_RED if i == 3 else
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

    def __print_word(word):
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
            print(ansi.bold("", persist=True), end="")
            terminal.tgfx_print_text(word, pos_x, pos_y + 1)
            print(terminal.ESCAPE_RESET_GRAPHICS, end="")
            terminal.tgfx_print_text("> ", pos_x, pos_y + 3)
            terminal.tgfx_print_text("======================================", pos_x, pos_y + 4)
            terminal.put_cursor_to(pos_x + 3, height / 2 + 3)
        else:
            print("TYPE THE WORD BELOW THEN PRESS [Enter]")
            print(word)
            print("> ", end="")

    def __print_congrats(time_taken, score, judgement_table):
        procedures_list = [
            procedures.defproc(1, "View Score Table", lambda: __view_score_table(time_taken, score, judgement_table)),
            procedures.defproc(0, "Exit", None)
        ]

        after_header = str(ansi.fgcolor(ansi.bold("Congratulations! You took {:.2f} seconds to type all words.".format(time_taken)),
                                        terminal.COLOR_YELLOW))
        after_header += "\n\n"
        after_header += str(ansi.fgcolor(ansi.bold("Your score is {:d}. Nice!!".format(score)), terminal.COLOR_YELLOW))

        before_header = None
        while True:
            status_code, option = procedures.print_ask_execute_procedures(str(ansi.fgcolor(ansi.bold("CONGRATULATIONS!!"), terminal.COLOR_YELLOW)),
                                                                          "+",
                                                                          procedures_list,
                                                                          status_footer=before_header,
                                                                          after_header=after_header,
                                                                          header_offset=-len(str(
                                                                              ansi.fgcolor(ansi.bold(""), terminal.COLOR_YELLOW)))+2)
            if status_code != STATUS_SUCCESS:
                before_header = "Invalid option."
                continue

            break

    def __view_score_table(time_taken, score, judgement_table):

        pass

    def game():
        status_code = __validate_invariants()

        if status_code != STATUS_SUCCESS:
            print_error(f"The game could not be started: {STATUS_CODE_TO_LITERAL_TABLE[status_code]}")
            return

        status_code, words = __build_word_sequence()

        if status_code != STATUS_SUCCESS:
            print_error(f"The game could not be started: {STATUS_CODE_TO_LITERAL_TABLE[status_code]}")
            return

        __print_countdown()

        timestamp_start = time.time()
        user_typed_words = []
        for word in words:
            __print_word(word)

            user_input = input()
            user_typed_words.append(user_input)

        terminal.erase_whole_screen()
        terminal.reset_cursor_to_top_left()

        time_taken = time.time() - timestamp_start
        status_code, score, judgement_table = __judge(words, user_typed_words)
        if status_code == STATUS_SUCCESS:
            __print_congrats(time_taken, score, judgement_table)
        else:
            print_error(f"The score could not be calculated: {status_code}")


    def destroy():
        pass

    return {
        "init": init,
        "run": run,
        "destroy": destroy
    }