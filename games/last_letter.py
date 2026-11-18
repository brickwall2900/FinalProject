from status import *

import procedures
import dialog
import terminal
import ansi
import persistence

from data import word_bank

import time
import random

from common import *

# inspired by that one ropblox game i played
RULES = "Last letter is a multiplayer game. Every last letter counts. Come up with words that have the first or last letter! Last one standing alive wins."
LETTER_START        = 0
LETTER_END          = 1

def last_letter():
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
            procedures.defproc(1, "PLAY!!!", game),
            procedures.defproc(2, "About", __about),
            procedures.defproc(0, "Exit", None)
        ]

        status_footer = None
        procedure_offset = 0
        while True:
            status_code, option, _ = procedures.ask_procedure("Last Letter", ",.",
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
    
    def __about():
        dialog.alert("Hi")

    BOT_NAMES = ["Computer", "Robot", "Bot", "AI", "CPU", "Agent", "Claude 0.1 ", "ChatGPT 1 ", "Pythonista"]

    def game():
        players = [] # a list of dicts (player data)

        def setup_player(id):
            player_data = {}

            player_name_or_bot = dialog.input("What is your name? Leave empty for bot.", f"Name for Player {id}")
            if player_name_or_bot is None or len(player_name_or_bot) == 0:
                player_data["name"] = pick_randomly(BOT_NAMES) + str(id)
                player_data["real"] = False
                player_data["bot_skill"] = random.random()
            else:
                player_data["name"] = player_name_or_bot
                player_data["real"] = True

            player_data["score"] = 0
            player_data["lives"] = 3
            return player_data

        def count(players, is_a_bot):
            number = 0
            for player in players:
                if (is_a_bot and not player["real"]) or (not is_a_bot and player["real"]):
                    number += 1
            return number


        number_of_players = None
        while number_of_players is None:
            number_of_players_raw = dialog.input("Give the number of players that will be playing.", "Last Letter")
            number_of_players = safeint(number_of_players_raw)
            if number_of_players is not None and number_of_players < 2:
                print_error("Cannot have less than two players.", "Last Letter")
                number_of_players = None # whoops

        for id in range(number_of_players):
            players.append(setup_player(id))

        dialog.alert("You can either have two or more keyboards connected to the same computer albeit with sabotage...\n \nOR\n \n" \
        "share one keyboard... albeit with contention.", "Play INFO")

        dialog.alert(f"Players: {count(players, False)} / Bots: {count(players, True)}\n \nAre ya'll ready?", "Play INFO")

        __core_game_loop(players)

    def __core_game_loop(players):
        previous_word = None
        time_seconds = 10
        prev_player_finish_time = None
        words_used = []
        message = None
        ranking = len(players)

        while ranking > 1:
            for player in players:
                if ranking <= 1:
                    break

                if player["lives"] <= 0:
                    continue

                # pick a letter first
                start_or_end, letters = __pick_letter(previous_word)

                name = player["name"]
                is_a_bot = not player["real"]

                judge_timestamp = time.time()
                yay = False
                while True: # turn would not end until player gets a correct word
                    if player["lives"] <= 0:
                        break

                    __print_letter(start_or_end, letters, name, is_a_bot, player["lives"], 10 - (time.time() - judge_timestamp), message)

                    word = None
                    if is_a_bot:
                        time.sleep(1)
                        word = __bot_turn(start_or_end, letters, player["bot_skill"], player)
                    else:
                        word = __player_turn(start_or_end, letters)

                    time_taken = (time.time() - judge_timestamp)
                    if time_taken > time_seconds: # timed out
                        message = f"{name} timed out!"
                        break

                    # judge time
                    okay1 = word is not None and find(words_used, word) is None
                    okay2 = word is not None and word_bank.can_word_be_found(word)
                    okay3 = word is not None and (str.startswith(word, letters) if start_or_end == LETTER_START else str.endswith(word, letters))
                    if okay1 and okay2 and okay3 and word is not None:
                        player["score"] += len(word) * 50
                        yay = True
                        prev_player_finish_time = time_taken
                        words_used.append(word)
                        message = ansi.fgcolor(f"{name} took {prev_player_finish_time:.2f} seconds to finish!", terminal.COLOR_GREEN)
                        break
                    elif word is not None:
                        player["lives"] -= 1
                        if not okay1:
                            message = "You used an already submitted word! \"" + ansi.fgcolor(word, terminal.COLOR_RED) + "\""
                        elif not okay2 or not okay3:
                            message = "You submitted an input that is not a word found in the word bank."

                if not yay: # nay
                    player["lives"] -= 1

                if player["lives"] <= 0:
                    message = ansi.bgcolor(ansi.fgcolor(f"Uh-oh! {name} ran out of lives and lost...", terminal.COLOR_WHITE), terminal.COLOR_RED)
                    player["ranking"] = ranking
                    ranking -= 1

        # last one standing wins rank 1
        for player in players:
            if "ranking" not in player:
                player["ranking"] = 1

        __show_leaderboard(players)

    def __show_leaderboard(players):
        # sort them as well
        def leaderboard_comparator(this, that):
            return this["ranking"] - that["ranking"]
        sort(players, leaderboard_comparator)

        # third is make it all procedures
        procedure_list = [
            procedures.defproc(0, "Exit", None)
        ]
        for i in range(len(players)):
            player = players[i]
            procedure_list.append(procedures.defproc(i + 1, f"{player["name"]}, {player["score"] if player["score"] is not None else "Unknown":.2f} pts", None))

        status_footer = None
        procedure_offset = 0
        while True:
            status_code, option_or_page, _ = procedures.ask_procedure("Leaderboard",
                                                    "v",
                                                    procedure_list,
                                                    after_header="GAME OVER!",
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

    # returns tuple (LETTER_START | LETTER_END, <chars>)
    def __pick_letter(previous_word):
        start_or_end = LETTER_START if randbool() else LETTER_END

        # then chars
        # it needs to be something from the dictionary
        # that means we will try solving it first
        if previous_word is None:
            previous_word = word_bank.get_random_word()

        assert previous_word is not None

        # then try slicing it, max of 4 chars, min of 1 char
        max_chars = [x for x in range(1, 5, 1)]
        chars_to_slice_list = max_chars.copy()
        candidate_letters_percentage = {}
        shuffle(chars_to_slice_list) # fix this algorith TODO FIXME
        for word in word_bank.words:
            for chars_to_slice in chars_to_slice_list:
                chosen_letters = None
                if len(previous_word) >= chars_to_slice:
                    if start_or_end == LETTER_START:
                        chosen_letters = previous_word[:chars_to_slice]
                    else:
                        chosen_letters = previous_word[-chars_to_slice:]
                else:
                    chosen_letters = previous_word

                # we have chosen our candidate word
                # now we check if we can like choose the majority of the words in it
                # we want to make the game easy and fun
                # so what we do is compare what we chose against the word bank and calc
                # how many % the words start/end with teh candidate letter

                # fucking linear search with possible 1+ mil elements
                total_word_count = len(word_bank.words)
                accepted_word_count = 0
            
                if start_or_end == LETTER_START:
                    if str.startswith(word, chosen_letters):
                        accepted_word_count += 1
                else:
                    if str.endswith(word, chosen_letters):
                        accepted_word_count += 1

                percentage = accepted_word_count / total_word_count
                candidate_letters_percentage[chars_to_slice] = percentage

        # then what do we do?
        # what if...

        # home of the mosdt inefficient algorithms out there
        sorted_easiest_to_hardest = []
        while len(sorted_easiest_to_hardest) < len(chars_to_slice_list):
            max = None
            max_i = None
            for i in range(len(chars_to_slice_list)):
                letter = chars_to_slice_list[i]
                if find(sorted_easiest_to_hardest, letter) is not None:
                    continue

                percentage = candidate_letters_percentage[letter]
                if max is None or max < percentage:
                    max_i = i
                    max = percentage

            sorted_easiest_to_hardest.append(max_i)

        chosen_letter_count_idx = random.choices(sorted_easiest_to_hardest, weights=max_chars, k=1)
        chosen_letter_count = chars_to_slice_list[chosen_letter_count_idx[0]]
        # ouch...
        chosen_letters = None
        if len(previous_word) >= chosen_letter_count:
            if start_or_end == LETTER_START:
                chosen_letters = previous_word[:chosen_letter_count]
            else:
                chosen_letters = previous_word[-chosen_letter_count:]
        else:
            chosen_letters = previous_word

        return (start_or_end, chosen_letters)

    def __print_letter(start_or_end, letters, name, is_bot, lives, time_left, message):
        s0 = f"Player {name} {"(Bot)" if is_bot else ""}; ({lives}/3) lives {time_left:.2f} s left!"
        s1 = f"TYPE THE WORD {"STARTING" if start_or_end == LETTER_START else "ENDING"} WITH"
        s2 = (letters + ("_" * clamp(10 - len(letters), 0, 10))) if start_or_end == LETTER_START else (("_" * clamp(10 - len(letters), 0, 10)) + letters)
        if terminal.use_advanced_terminal_graphics:
            terminal.erase_whole_screen()
            terminal.reset_cursor_to_top_left()
            max_width = max(terminal.get_string_visual_width(s0),
                            terminal.get_string_visual_width(s1),
                            terminal.get_string_visual_width(s2),
                            terminal.get_string_visual_width(message) if message is not None else 0)

            width = terminal.get_width()
            height = terminal.get_height()
            pos_x = width / 2 - max_width / 2
            pos_y = height / 2
            dialog_width = max_width

            terminal.tgfx_print_text(s0, pos_x, pos_y - 2)
            terminal.tgfx_print_text("=" * dialog_width, pos_x, pos_y - 1)
            terminal.tgfx_print_text(s1, pos_x + dialog_width/2 - terminal.get_string_visual_width(s1)/2, pos_y)

            terminal.tgfx_print_text(ansi.underline(ansi.bold(s2)), pos_x + dialog_width/2 - terminal.get_string_visual_width(s2)/2, pos_y + 1)

            terminal.tgfx_print_text(f"> {ansi.bold("Bot is thinking...") if is_bot else ""}", pos_x, pos_y + 3)
            terminal.tgfx_print_text("=" * dialog_width, pos_x, pos_y + 4)
            if message:
                terminal.tgfx_print_text(message, pos_x, pos_y + 5)
            terminal.put_cursor_to(pos_x + 3, height / 2 + 3)
        else:
            print(s0)
            print("----------------")
            print(s1)
            print(s2)
            print(f"> {"Bot is thinking..." if is_bot else ""}", end="")
            if message:
                print(message)

        terminal.flush()

    # returns True if the player manages to get the word in time, False if the player runs out of time
    def __player_turn(start_or_end, letters):
        return input().strip().lower()

    def __bot_turn(start_or_end, letters, bot_difficulty, player_data):
        # bot difficulty
        # n - secs max / sluggishness secs
        # 0 - 12 / .7
        # 1 - 2 / .1
        seconds_budget = lerp(12, 2, bot_difficulty) + random.random() * 2 * (-1 if randbool() else 1)
        sluggish = lerp(.7, .1, bot_difficulty)

        time_start_timestamp = time.time()
        chosen_word = None
        correct_word = None

        # ok solve
        while True:
            if (time.time() - time_start_timestamp) > seconds_budget:
                return None

            word = word_bank.get_random_word()
            if start_or_end == LETTER_START:
                if str.startswith(word, letters):
                    chosen_word = word
                    correct_word = word
                    break
            else:
                if str.endswith(word, letters):
                    chosen_word = word
                    correct_word = word
                    break

            time.sleep(clamp(random.random() * sluggish, 0, seconds_budget - (time.time() - time_start_timestamp)))

        player_data["bot_correct_word"] = correct_word
        # how the fuck can i artifically mess upthe bot

        return chosen_word
        

    def destroy():
        pass

    return {
        "init": init,
        "run": run,
        "destroy": destroy
    }