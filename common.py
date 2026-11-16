# Utility functions
import ansi
import terminal
import random

import os

import dialog
from status import STATUS_INDEX_OUT_OF_BOUNDS, STATUS_SUCCESS

# safeint() functions equivalently like int(), but returns `None` on invalid input.
def safeint(given, default=None):
    if str.isdigit(given) and str.isascii(given):
        return int(given)
    else:
        return default

def safefloat(given, default=None):
    valid = True

    if not isinstance(given, str):
        return default

    given = given.strip().lower()

    test = given
    if test.startswith("+") or test.startswith("-"):
        test = test[1:]

    if test.count("e") > 1 or test.count(".") > 1:
        return default

    if "e" in test:
        _, part2 = test.split("e")
        if part2.startswith("+") or part2.startswith("-"):
            part2 = part2[1:]
        if not (part2.isascii() and part2.isdigit()):
            return default

    test = test.replace(".", "")
    if test.isdigit() and test.isascii():
        return float(given)
    else:
        return default
    


# Swaps two items in a list in-place.
def swap(the_list, a, b):
    size = len(the_list)
    if a < 0 or a >= size or b < 0 or b >= size:
        return STATUS_INDEX_OUT_OF_BOUNDS

    tmp = the_list[a]
    the_list[a] = the_list[b]
    the_list[b] = tmp

    return STATUS_SUCCESS

# Sorts a given list using a given comparator function
# selection sort, please change to something more "performative"
# selection sort is the most simplest thing i've thought of and i have no sleep
def sort(the_list, comparator):
    for i in range(len(the_list)):
        min = i
        for j in range(i + 1, len(the_list)):
            if comparator(the_list[min], the_list[j]) > 0: # this > that
                min = j
        swap(the_list, i, min)

def find(haystack, needle):
    for i in range(len(haystack)):
        if haystack[i] == needle:
            return i

    return None

# Shuffles a list in-place
# i implemented my own for aura points
def shuffle(the_list):
    size = len(the_list)
    for i in range(size):
        new_index = random.randint(0, size)
        swap(the_list, i, new_index)

# Forces a number to be within in range of [min, max].
def clamp(given, n_min, n_max):
    return max(min(given, n_max), n_min)

# Converts a string to a boolean
def str_to_bool(given):
    if given is None:
        return False

    if not isinstance(given, str):
        return False

    return given.strip().lower() == "true"

# Returns the number of digits in a number
def get_digits(number):
    digit_count = 0
    while True:
        quotient = number // 10
        if quotient is not 0:
            digit_count += 1
        else:
            break
        number = quotient
    return digit_count + 1

SUICIDAL = str_to_bool(os.environ.get("SUICIDAL", "False"))

# Prints an error on the screen with a distinct text color of red.
def print_error(value, end="\n"):
    option = dialog.alert(ansi.bold(ansi.fgcolor(str(value), terminal.COLOR_RED)), 
                 ansi.bgcolor(ansi.fgcolor(ansi.bold("Error"), terminal.COLOR_WHITE), terminal.COLOR_RED),
                 ["OK", "Commit Suicide"] if SUICIDAL else ["OK"], "OK")
    if option == "Commit Suicide":
        raise SystemError()

def print_separator(c="*", count=20):
    print(c * count)