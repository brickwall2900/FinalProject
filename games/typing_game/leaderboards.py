from common import print_error, safeint, sort, get_whole_digits
import persistence

def save_to_leaderboard(time_taken, score, judgement_table):
    name = input("What is your name? ")
    # hmmm
    # FIXME: my prefrontal cortex is shut down
    # fuck

    leaderboard = persistence.load_persistence("leaderboard-typing_game")
    current_entry = 0

    if leaderboard is not None:
        current_entry = safeint(leaderboard.get("CurrentEntry"), 0)
        current_entry += 1

        leaderboard["CurrentEntry"] = str(current_entry)
    else:
        leaderboard = {}
        leaderboard["CurrentEntry"] = "0"
    
    leaderboard[f"Entry{current_entry}"] = name
    leaderboard[f"Entry{current_entry}_time_taken"] = str(int(time_taken * 100))
    leaderboard[f"Entry{current_entry}_score"] = str(score)
    leaderboard[f"Entry{current_entry}_judgement_count"] = str(len(judgement_table))

    for index in range(len(judgement_table)):
        entry = judgement_table[index]
        leaderboard[f"Entry{current_entry}_judgement_{index}_correct"] = entry[0]
        leaderboard[f"Entry{current_entry}_judgement_{index}_user"] = entry[1]
        leaderboard[f"Entry{current_entry}_judgement_{index}_score"] = str(entry[2])

    persistence.save_persistence("leaderboard-typing_game", leaderboard)

    view_leaderboard()

def __leaderboard_comparator(this, that):
    this_score = this[2]
    that_score = that[2]
    if this_score != that_score:
        return (that_score - this_score)
    else: # if same score, compare by time instead.
        this_time = this[1]
        that_time = that[1]
        return (this_time - that_time)

def __parse_leaderboard(loaded_leaderboard):
    the_leaderboard = []

    entry_count = safeint(loaded_leaderboard.get("CurrentEntry"), 0)

    for i in range(entry_count + 1):
        entry_key = f"Entry{i}"

        name = loaded_leaderboard.get(entry_key)
        if name is None:
            continue

        time = safeint(loaded_leaderboard.get(entry_key + "_time_taken"))
        score = safeint(loaded_leaderboard.get(entry_key + "_score"))
        judgement_table_count = safeint(loaded_leaderboard.get(entry_key + "_judgement_count"))

        if time is None or score is None or judgement_table_count is None:
            continue

        time = time / 100 # compensate float to int by division by 100

        missing = False
        judgement_table = []
        for judgement_table_index in range(judgement_table_count):
            judgement_entry_key = entry_key + f"_judgement_{judgement_table_index}"
            correct_word = loaded_leaderboard.get(judgement_entry_key + "_correct")
            user_typed_word = loaded_leaderboard.get(judgement_entry_key + "_user")
            word_score = safeint(loaded_leaderboard.get(judgement_entry_key + "_score"))

            if correct_word is None or user_typed_word is None or word_score is None:
                missing = True
                break
            judgement_table.append((correct_word, user_typed_word, word_score))

        if missing:
            continue

        the_leaderboard.append((name, time, score, judgement_table))

    return the_leaderboard

def __paginate_and_navigate_leaderboard(leaderboard):
    page_offset = 0
    page_count = len(leaderboard)
    max_page_view = 10
    message = ""

    while True:
        print(" ^^^ Leaderboard ^^^")
        page_end = min(page_count, page_offset + max_page_view)
        items_on_page = page_end - page_offset

        for index in range(page_offset, page_end):
            entry = leaderboard[index]
            name = entry[0]
            time = entry[1]
            score = entry[2]

            print(f" - [{(index - page_offset) + 1}]: {name}; {time} seconds; {score} pts.")

        show_prev = page_offset > 0
        show_next = page_end < page_count

        print()
        if show_prev:
            print(" - [Q]: Previous")
        if show_next:
            print(" - [W]: Next")
        print(" - [0]: Exit")
        print(message)
        raw_chosen = input("> ").lower().strip()
        chosen = safeint(raw_chosen)
        message = ""

        if chosen is None:
            if raw_chosen.startswith("q") and show_prev:
                page_offset = page_offset - max_page_view
            elif raw_chosen.startswith("w") and show_next:
                page_offset = page_offset + max_page_view
            else:
                message = "Invalid option, try again."
            continue

        if chosen == 0:
            break
        else:
            if not (1 <= chosen <= items_on_page):
                message = "Invalid option, try again."
                continue
            real_index = page_offset + (chosen - 1)
            leaderboard_entry = leaderboard[real_index]
            view_score_table(leaderboard_entry[3], leaderboard_entry[0])

def view_leaderboard():
    loaded_leaderboard = persistence.load_persistence("leaderboard-typing_game")

    if loaded_leaderboard is None:
        print_error("Leaderboard cannot be loaded because you haven't played a game yet, or because of file corruption.")
        return

    the_leaderboard = __parse_leaderboard(loaded_leaderboard)

    sort(the_leaderboard, __leaderboard_comparator)

    __paginate_and_navigate_leaderboard(the_leaderboard)

def view_score_table(judgement_table, name=None):
    # (correct_word, user_input_word, score)
    page_offset = 0
    page_count = len(judgement_table)
    max_page_view = 10
    message = ""

    while True:
        print(f" ^^^ Viewing scores{ (' for ' + name) if name is not None else ''} ^^^")
        
        longest_correct_word = 0
        longest_user_word = 0
        for entry in judgement_table:
            longest_correct_word = len(entry[0]) if len(entry[0]) > longest_correct_word else longest_correct_word
            longest_user_word = len(entry[1]) if len(entry[1]) > longest_user_word else longest_user_word
        longest_correct_word += 1
        longest_user_word += 1

        page_end = min(page_count, page_offset + max_page_view)
        items_on_page = page_end - page_offset
        
        for index in range(page_offset, page_end):
            entry = judgement_table[index]
            visual_index = index - page_offset + 1
            correct_word = entry[0] # type: str
            user_input_word = entry[1] # type: str
            score = entry[2]
            
            correct_word = correct_word.ljust(max(longest_correct_word - get_whole_digits(visual_index) + 1, 0))
            user_input_word = user_input_word.ljust(max(longest_user_word, 0))

            print(f" - [{visual_index}]: {correct_word} | {user_input_word}| +{score} pts.")

        show_prev = page_offset > 0
        show_next = page_end < page_count

        print()
        if show_prev:
            print(" - [Q]: Previous")
        if show_next:
            print(" - [W]: Next")
        print(" - [0]: Exit")
        print(message)
        raw_chosen = input("> ").lower().strip()
        chosen = safeint(raw_chosen)
        message = ""

        if chosen is None:
            if raw_chosen.startswith("q") and show_prev:
                page_offset = page_offset - max_page_view
            elif raw_chosen.startswith("w") and show_next:
                page_offset = page_offset + max_page_view
            else:
                message = "Invalid option, try again."
            continue

        if chosen == 0:
            break
