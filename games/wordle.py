from status import *

import procedures
import dialog
import terminal
import ansi
import persistence

from data import word_bank

import time
import random

from common import safeint, print_error, get_digits, clamp, find, safefloat, sort, str_to_bool, shuffle

RULES = "Wordle is an NYC-Times game that gives you 6 guesses to guess a 5-letter word."

def wordle():
    def init():
        status_code, word_count = word_bank.try_loading_words()
        success = (status_code == STATUS_SUCCESS
                    or status_code == STATUS_ALREADY_EXISTS)

        if not success:
            if status_code == STATUS_FILE_NOT_FOUND:
                print_error("Word bank not found. "
                            f"Please verify directory structure and that the word bank file exists.")
                return False

        return success

    def run():
        procedures_list = [
            procedures.defproc(1, "Start", game),
            procedures.defproc(2, "Daily Game", game),
            procedures.defproc(4, "About", __about),
            procedures.defproc(0, "Exit", None)
        ]

        status_footer = None
        procedure_offset = 0
        while True:
            status_code, option, _ = procedures.ask_procedure("WORDLE", ";",
                                                                            procedures_list,
                                                                            status_footer=status_footer,
                                                                            after_header=RULES,
                                                                            procedure_offset=procedure_offset)

            if status_code == STATUS_NEXT and option is not None:
                procedure_offset += option
                continue
            elif status_code == STATUS_PREVIOUS and option is not None:
                procedure_offset -= option
                continue
            
            status_code = procedures.do_execute_procedure(procedures_list, option)
            if status_code != STATUS_SUCCESS:
                status_footer = "Invalid option."
                continue
            else:
                status_footer = None

            if option == 0:  # exit option
                break
        pass
    

    # defines one instance of a wordle game
    def __wordle_game(letter_count, guesses):
        pass

    # picks a wordle word
    # - must be guessable
    def __pick_word(letter_count, guesses):
        words_already_picked = [] # words already randomly picked
        letter_count_words = word_bank.get_words_with_letter_count(letter_count)
        copy_words = letter_count_words.copy()

        shuffle(letter_count_words)

        # straight away, if there are less words than guesses then fail immediately
        if len(letter_count_words) < guesses:
            return STATUS_UNDERPOPULATED, None

        the_final_chosen_word = None
        while len(letter_count_words) > 0:
            chosen_word = letter_count_words.pop()
            # then we check if the word is guessable; aka find a set of words that could solve the wordle
            if __check_word_bank_if_guessable(letter_count, chosen_word, copy_words, guesses):
                the_final_chosen_word = chosen_word
                break

        # we failed to choose a final word; probably because the word bank is shit
        if the_final_chosen_word is None:
            return STATUS_BAD_USER_INPUT, None

        return STATUS_SUCCESS, the_final_chosen_word


    # checks the word bank if the word is guessable by the word bank alone
    def __check_word_bank_if_guessable(letter_count, the_word, other_words, guesses):
        

    def destroy():
        pass

    return {
        "init": init,
        "run": run,
        "destroy": destroy
    }