import os

import ansi
import terminal
from common import print_error, shuffle, str_to_bool, safeint, safefloat, sort, find
from data import word_bank
import persistence

import procedures
import dialog

import time
import random

from status import STATUS_UNDERPOPULATED, STATUS_SUCCESS, STATUS_ALREADY_EXISTS, STATUS_FILE_NOT_FOUND, \
    STATUS_CODE_TO_LITERAL_TABLE, STATUS_NEXT, STATUS_PREVIOUS

RULES = "The Typing Game tests your typing skills by you typing words with speed and accuracy!"

SETTINGS_DEFAULT = {
    "words_in_random": True,
    "show_words_in_advance": True,
    "letter_count_to_include": [3, 4, 5],
    "word_count_per_letter_count": { 3: 7, 4: 7, 5: 7 },
    "score_per_letter_count": { 3: 2, 4: 5, 5: 7 },
}

def typing_game():
    settings = {
        "words_in_random": SETTINGS_DEFAULT["words_in_random"],
        "show_words_in_advance": SETTINGS_DEFAULT["show_words_in_advance"],
        "letter_count_to_include": SETTINGS_DEFAULT["letter_count_to_include"],
        "word_count_per_letter_count": SETTINGS_DEFAULT["word_count_per_letter_count"],
        "score_per_letter_count": SETTINGS_DEFAULT["score_per_letter_count"],
    }

    def init():
        error_code, word_count = word_bank.try_loading_words()
        success = (error_code == STATUS_SUCCESS
                   or error_code == STATUS_ALREADY_EXISTS)

        if not success:
            if error_code == STATUS_FILE_NOT_FOUND:
                print_error("Word bank not found. "
                            f"Please verify directory structure and that the word bank file exists.")
                return False

        # load settings
        error_code, settings_loaded = persistence.load_persistence("typing_game")
        if error_code == STATUS_FILE_NOT_FOUND:
            __save_settings()
        elif error_code == STATUS_SUCCESS and settings_loaded is not None:
            if "WordsInRandom" in settings_loaded:
                settings["words_in_random"] = str_to_bool(settings_loaded["WordsInRandom"])

            if "ShowWordsInAdvance" in settings_loaded:
                settings["show_words_in_advance"] = str_to_bool(settings_loaded["ShowWordsInAdvance"])

            if "LetterCountToInclude" in settings_loaded:
                settings["letter_count_to_include"] = [x for x in [safeint(x) for x in str(settings_loaded["LetterCountToInclude"]).split(",")] if x is not None]

            for letter_count in settings.get("letter_count_to_include", SETTINGS_DEFAULT["letter_count_to_include"]):
                if f"WordCountPerLetterCount_{letter_count}" in settings_loaded:
                    value = safeint(settings_loaded[f"WordCountPerLetterCount_{letter_count}"])
                    if value is not None:
                        settings["word_count_per_letter_count"][letter_count] = value
                if f"ScorePerLetterCount_{letter_count}" in settings_loaded:
                    value = safeint(settings_loaded[f"ScorePerLetterCount_{letter_count}"])
                    if value is not None:
                        settings["score_per_letter_count"][letter_count] = value
        else:
            print_error("Settings file corrupt. Using default settings instead.")

        return success

    def run():
        procedures_list = [
            procedures.defproc(1, "Start", game),
            procedures.defproc(2, "Leaderboards", __view_leaderboard),
            procedures.defproc(3, "Settings", __settings),
            procedures.defproc(4, "About", __view_about),
            procedures.defproc(0, "Exit", None)
        ]

        status_footer = None
        procedure_offset = 0
        while True:
            status_code, option, _ = procedures.ask_procedure("Typing Game!!", "+",
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

    def __view_about():
        dialog.alert("The Typing Game tests how fast you can type words correctly!!" \
        " Type more words correctly, the more points you get. Better if you can type" \
        " words with speed and accuracy!", "About")

        dialog.alert("TLDR; Type correct words = more points\n \n" \
        "test\n \n> test (<- this is your input box)\n \n!! CORRECT !!", "About")

        dialog.alert("TLDR; Type correct words = more points\n \n" \
        "hello\n \n> henlo\n \n!! INCORRECT !! you get 0 points...", "About")

    def __get_setting(key):
        return settings.get(key, SETTINGS_DEFAULT[key])

    def __save_settings():
        saved_settings = {
            "WordsInRandom": str(__get_setting("words_in_random")),
            "ShowWordsInAdvance": str(__get_setting("show_words_in_advance")),
            "LetterCountToInclude": ",".join([str(x) for x in __get_setting("letter_count_to_include")]), # yeah i know what this shit does now
        }
        for letter_count in settings["letter_count_to_include"]:
            saved_settings[f"WordCountPerLetterCount_{letter_count}"] = str(__get_setting("word_count_per_letter_count")[letter_count])
            saved_settings[f"ScorePerLetterCount_{letter_count}"] = str(__get_setting("score_per_letter_count")[letter_count])

        persistence.save_persistence("typing_game", saved_settings)


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

        for letter_count in __get_setting("letter_count_to_include"):
            status_code, words = __pick_words(__get_setting("word_count_per_letter_count")[letter_count], letter_count)
            if status_code == STATUS_SUCCESS and words is not None:
                result.extend(words)
            else:
                assert status_code == STATUS_UNDERPOPULATED
                print_error(f"Insufficient words in word bank. Please provide more {letter_count}-letter words.")
                return status_code, None

        if __get_setting("words_in_random"):
            shuffle(result)

        return STATUS_SUCCESS, result

    def __validate_invariants():
        # thank goodness python is single-threaded or we are cooked.
        if len(__get_setting("letter_count_to_include")) <= 0:
            print_error("At least one n-letter count must be specified.")
            return STATUS_UNDERPOPULATED

        for letter_count in __get_setting("letter_count_to_include"):
            if not letter_count in __get_setting("word_count_per_letter_count"):
                print_error(f"The word count for {letter_count}-letter words is unspecified.")
                return STATUS_UNDERPOPULATED

            if not letter_count in __get_setting("score_per_letter_count"):
                print_error(f"The score for {letter_count}-letter words is unspecified.")
                return STATUS_UNDERPOPULATED

        return STATUS_SUCCESS

    def __judge(correct_input_list, user_input_list):
        if len(correct_input_list) < len(user_input_list):
            return STATUS_UNDERPOPULATED, 0, []

        # list of tuples (correct_word, user_input_word, score)
        judgement_table = []
        score = 0
        for i in range(len(correct_input_list)):
            correct_input = correct_input_list[i]
            user_input = user_input_list[i]
            letter_count = len(correct_input)
            if not letter_count in __get_setting("score_per_letter_count"):
                print_error(f"Score per {letter_count}-letter word is missing right now... How come?")
                return STATUS_UNDERPOPULATED, 0, []
            given_score = __get_setting("score_per_letter_count")[letter_count]
            if correct_input == user_input:
                score += given_score
            judgement_table.append((correct_input, user_input, (given_score if correct_input == user_input else 0)))

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

    def __print_word(word, future_words):
        if terminal.use_advanced_terminal_graphics:
            terminal.erase_whole_screen()
            terminal.reset_cursor_to_top_left()
            max_width = max(terminal.get_string_visual_width("TYPE THE WORD BELOW THEN PRESS [Enter]"),
                            terminal.get_string_visual_width(word))

            width = terminal.get_width()
            height = terminal.get_height()
            pos_x = width / 2 - max_width / 2
            pos_y = height / 2
            dialog_width = len("======================================")

            terminal.tgfx_print_text("=" * dialog_width, pos_x, pos_y - 1)
            terminal.tgfx_print_text("TYPE THE WORD BELOW THEN PRESS [Enter]", pos_x, pos_y)

            word_x = pos_x
            terminal.tgfx_print_text(ansi.underline(ansi.bold(word)), word_x, pos_y + 1)
            word_x += len(ansi.get_raw_string(word)) + 1

            if __get_setting("show_words_in_advance"):
                future_word_length = 0
                for future in future_words:
                    length = len(ansi.get_raw_string(future)) + 1
                    future_word_length += length
                    if future_word_length > dialog_width:
                        break
                    terminal.tgfx_print_text(ansi.bold(future), word_x + future_word_length - length, pos_y + 1)

            terminal.tgfx_print_text(">", pos_x, pos_y + 3)
            terminal.tgfx_print_text("=" * dialog_width, pos_x, pos_y + 4)
            terminal.put_cursor_to(pos_x + 3, height / 2 + 3)
        else:
            print("TYPE THE WORD BELOW THEN PRESS [Enter]")
            print(f">> {word} << {" ".join([future_words[i] for i in range(len(future_words)) if i < 5]) if __get_setting("show_words_in_advance") else ""}")
            print("> ", end="")

    def __print_congrats(time_taken, score, judgement_table):
        procedures_list = [
            procedures.defproc(1, "View Score Table", lambda: __view_score_table(time_taken, score, judgement_table)),
            procedures.defproc(2, "Submit to Leaderboard", lambda: __save_to_leaderboard(time_taken, score, judgement_table)),
            procedures.defproc(0, "Exit", None)
        ]

        after_header = str(ansi.fgcolor(ansi.bold("Congratulations! You took {:.2f} seconds to type all words.".format(time_taken)),
                                        terminal.COLOR_YELLOW))
        after_header += "\n\n"
        after_header += str(ansi.fgcolor(ansi.bold("Your score is {:d}. Good job!".format(score)), terminal.COLOR_YELLOW))

        before_header = None

        submitted_to_leaderboard = False
        while True:
            _, option, _ = procedures.ask_procedure((ansi.fgcolor(ansi.bold("CONGRATULATIONS!!"), terminal.COLOR_YELLOW)) if terminal.use_advanced_terminal_graphics else "CONGRATULATIONS!!",
                                                 "+",
                                                 procedures_list,
                                                 status_footer=before_header,
                                                 after_header=after_header if terminal.use_advanced_terminal_graphics else ansi.get_raw_string(after_header))

            if option == 2:
                if submitted_to_leaderboard:
                    before_header = "Already submitted."
                    continue
                else:
                    submitted_to_leaderboard = True
                    before_header = "Submitted!"

            status_code = procedures.do_execute_procedure(procedures_list, option)
            if status_code != STATUS_SUCCESS:
                before_header = "Invalid option."
                continue

            if option == 0:
                break # exit

    def __save_to_leaderboard(time_taken, score, judgement_table):
        name = dialog.input("What is your name?")
        assert name is not None
        name = name.replace(",", "")

        # list incomprehension
        serialized_judgement_table = "::".join([f"({"".join(x for x in x[0] if x.isalpha())}|{"".join(x for x in x[1] if x.isalpha())}|{x[2]})" for x in judgement_table])
        new_entry = f"{name},{time_taken},{score},{serialized_judgement_table}"

        status_code, leaderboard = persistence.load_persistence("leaderboard-typing_game")
        if status_code == STATUS_SUCCESS and leaderboard is not None:
            nextEntry = safeint(leaderboard.get("NextEntry", "1")) or 1
            nextEntry += 1

            leaderboard["NextEntry"] = str(nextEntry)
            leaderboard[f"Entry{nextEntry}"] = new_entry
        else:
            leaderboard = {}
            leaderboard["NextEntry"] = 1
            leaderboard[f"Entry{leaderboard["NextEntry"]}"] = new_entry

        persistence.save_persistence("leaderboard-typing_game", leaderboard)

        __view_leaderboard()

    def __view_leaderboard():
        status_code, leaderboard = persistence.load_persistence("leaderboard-typing_game")
        if status_code == STATUS_FILE_NOT_FOUND:
            print_error("Leaderbord has not been created yet. Play a game first then submit a run to the leaderboard!")
            return

        if status_code != STATUS_SUCCESS or leaderboard is None:
            print_error("Leaderboard cannot be loaded because of file corruption.")
            return

        # first step in loading the leaderboard, get the number of entries
        entry_count = safeint(leaderboard.get("NextEntry", "1")) or 1

        # second step is iterate and parse through entries
        real_leaderboard = []
        for i in range(entry_count+1):
            entry = leaderboard.get(f"Entry{i+1}")
            if entry is None:
                continue

            parsed_entry = entry.split(",")
            if len(parsed_entry) != 4: # terminate immediately
                continue
            name, time, score = parsed_entry[0], parsed_entry[1], parsed_entry[2]
            judgement_table_serialized = parsed_entry[3]

            real_leaderboard.append((name, safefloat(time), safeint(score), judgement_table_serialized))

        # sort them as well
        def leaderboard_comparator(this, that):
            return that[2] - this[2]
        sort(real_leaderboard, leaderboard_comparator)

        # third is make it all procedures
        procedure_list = [
            procedures.defproc(0, "Exit", None)
        ]
        for i in range(len(real_leaderboard)):
            entry = real_leaderboard[i]
            procedure_list.append(procedures.defproc(i + 1, f"{entry[0]}, {entry[2] if entry[2] is not None else "Unknown"} pts, {entry[1] if entry[1] is not None else "Unknown":.2f} secs",
                                                     lambda entry=entry: __view_score_table(entry[1], entry[2], __parse_serialized_judgement_table(entry[3]), entry[0])))

        status_footer = None
        procedure_offset = 0
        while True:
            status_code, option_or_page, _ = procedures.ask_procedure("Leaderboard",
                                                    "v",
                                                    procedure_list,
                                                    status_footer=status_footer,
                                                    procedure_offset=procedure_offset,
                                                    procedure_limit=10)

            if status_code == STATUS_SUCCESS and option_or_page == 0:
                break # exit

            if status_code == STATUS_NEXT and option_or_page:
                procedure_offset += option_or_page
                continue
            elif status_code == STATUS_PREVIOUS and option_or_page:
                procedure_offset -= option_or_page
                continue

            status_code = procedures.do_execute_procedure(procedure_list, option_or_page)
            
            if status_code != STATUS_SUCCESS:
                status_footer = "Invalid option."
                continue

    def __parse_serialized_judgement_table(serialized):
        table_entries = str(serialized).split("::")
        judgement_table = []
        for x in table_entries:
            x = x[1:-1]
            entry = x.split("|")
            judgement_table.append((entry[0], entry[1], safeint(entry[2])))

        return judgement_table


    def __view_score_table(time_taken, score, judgement_table, name=None):
        # (correct_word, user_input_word, score)
        procedure_list = [
            procedures.defproc(0, "Exit", None)
        ]

        for i in range(len(judgement_table)):
            entry = judgement_table[i]
            procedure_list.append(procedures.defproc(i+1, f"{entry[0]} | {entry[1]} | +{entry[2]}", None))

        
        status_footer = None
        procedure_offset = 0
        while True:
            status_code, option_or_page, _ = procedures.ask_procedure(f"Viewing scores for {name}" if name is not None else "Viewing scores",
                                                    "$",
                                                    procedure_list,
                                                    after_header="\n<correct> | <you typed> | <score>",
                                                    status_footer=status_footer,
                                                    procedure_offset=procedure_offset,
                                                    procedure_limit=10)

            if status_code == STATUS_SUCCESS and option_or_page == 0:
                break # exit

            if status_code == STATUS_NEXT and option_or_page:
                procedure_offset += option_or_page
                continue
            elif status_code == STATUS_PREVIOUS and option_or_page:
                procedure_offset -= option_or_page
                continue

    def game():
        status_code = __validate_invariants()

        if status_code != STATUS_SUCCESS:
            print_error(f"The game could not be started: {STATUS_CODE_TO_LITERAL_TABLE[status_code]}")
            return

        status_code, words = __build_word_sequence()

        if status_code != STATUS_SUCCESS or words is None:
            print_error(f"The game could not be started: {STATUS_CODE_TO_LITERAL_TABLE[status_code]}")
            return

        __print_countdown()

        timestamp_start = time.time()
        user_typed_words = []
        for i in range(len(words)):
            word = words[i]
            __print_word(word, words[i+1:])

            user_input = input()
            user_typed_words.append(user_input)

        terminal.erase_whole_screen()
        terminal.reset_cursor_to_top_left()

        time_taken = time.time() - timestamp_start
        status_code, score, judgement_table = __judge(words, user_typed_words)
        if status_code == STATUS_SUCCESS:
            __print_congrats(time_taken, score, judgement_table)
        else:
            print_error(f"The score could not be calculated: {STATUS_CODE_TO_LITERAL_TABLE[status_code]}")


    def destroy(): # do nothing on destroy
        pass

    # UMM OKAY NOTE
    # there has to be a better way to do this shit
    # I owe an apology to the professors whom they will be reviewing this code.
    def __settings():
        def boolean_setting(key, name, description):
            def proc():
                
                procedures_list = [
                    procedures.defproc(1, "Toggle", None),
                    procedures.defproc(0, "Go Back", None)
                ]
    
                description_display = f"{description}\n \nCurrent value: {str(__get_setting(key)).upper()}"
    
                while True:
                    status_code, option, _ = procedures.ask_procedure(name, "?",
                                                            procedures_list,
                                                            after_header=description_display)
                    if status_code == STATUS_SUCCESS:
                        if option == 0:
                            break
                        elif option == 1:
                            settings[key] = not __get_setting(key)
    
                    description_display = f"{description}\n \nCurrent value: {str(__get_setting(key)).upper()}"

            return proc

        def __opt_letter_counts():
            procedures_list = [
                procedures.defproc(1, "Add", None),
                procedures.defproc(2, "Remove", None),
                procedures.defproc(0, "Go Back", None)
            ]

            description = f"Letter counts.\n \nCurrent value: {str(__get_setting("letter_count_to_include")).upper()}"

            while True:
                status_code, option, _ = procedures.ask_procedure("Letter counts", "?",
                                                        procedures_list,
                                                        after_header=description)
                if status_code == STATUS_SUCCESS:
                    if option == 0:
                        break
                    elif option == 1:
                        count = dialog.input("How many letters?", "Letter counts")
                        count = safeint(count)
                        if count is not None and find(__get_setting("letter_count_to_include"), count) is None:
                            __get_setting("letter_count_to_include").append(count)
                        else:
                            print_error("Letter count is invalid or already included.")
                    elif option == 2:
                        count = dialog.input(f"Specify letter count to remove? ({__get_setting("letter_count_to_include")})", "Letter counts")
                        count = safeint(count)
                        if count is not None and find(__get_setting("letter_count_to_include"), count) is not None:
                            __get_setting("letter_count_to_include").remove(count)
                        else:
                            print_error("Letter count is invalid or not in the list.")

                description = f"Letter counts.\n \nCurrent value: {str(__get_setting("letter_count_to_include")).upper()}"

        def letter_setting(key, title, description):
            def proc():
                def __edit_for_letter_count(letter_count):
                    def proc():
                        new_value = dialog.input(f"{description} (for {letter_count}-letter words).\n \nCurrent: {__get_setting(key)[letter_count]}")
                        new_value = safeint(new_value)
                        if new_value:
                            __get_setting(key)[letter_count] = new_value
                        else:
                            print_error("Bad value specified.")
                    return proc

                procedures_list = [
                    procedures.defproc(0, "Go Back", None)
                ]

                item = 1
                for k in __get_setting(key).keys():
                    procedures_list.append(procedures.defproc(item, f"{k}-letter words", __edit_for_letter_count(k)))
                    item += 1

                status_footer = None
                while True:
                    status_code, option, _ = procedures.ask_procedure(title, "?",
                                                            procedures_list,
                                                            after_header="Choose the letter count",
                                                            status_footer=status_footer)

                    if status_code != STATUS_SUCCESS:
                        status_footer = "Invalid option."
                        continue
                    else:
                        status_footer = None
        
                    if option == 0:  # exit option
                        break

                    procedures.do_execute_procedure(procedures_list, option)
            return proc

        procedures_list = [
            procedures.defproc(1, "Words shuffled randomly", boolean_setting("words_in_random", "Words shuffled randomly", "Words are shuffled in-game. If TRUE, next words are shuffled. Otherwise, words appear in letter-count order.")),
            procedures.defproc(2, "Show words in advance", boolean_setting("show_words_in_advance", "Show words in advance", "Show next words that will be typed.")),
            procedures.defproc(3, "Letter counts", __opt_letter_counts),
            procedures.defproc(4, "Word counts", letter_setting("word_count_per_letter_count", "Word counts", "Choose the number of times these number of words appear in a game.")),
            procedures.defproc(5, "Score per letter count", letter_setting("score_per_letter_count", "Score per letter count", "Choose how much score given for these number of words if typed correctly")),
            procedures.defproc(0, "Exit", None)
        ]

        status_footer = None
        procedure_offset = 0
        while True:
            status_code, option, _ = procedures.ask_procedure("Settings", "?",
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
                __save_settings()
                break

    return {
        "init": init,
        "run": run,
        "destroy": destroy
    }