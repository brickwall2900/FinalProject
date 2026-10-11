# Utility functions
import ansi
import random

from status import STATUS_INDEX_OUT_OF_BOUNDS, STATUS_SUCCESS

# safeint() functions equivalently like int(), but returns `None` on invalid input.
def safeint(given, default=None):
    if str.isdigit(given):
        return int(given)
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

# Shuffles a list in-place
# i implemented my own for aura points
def shuffle(the_list):
    size = len(the_list)
    for i in range(size):
        new_index = random.randint(0, size)
        swap(the_list, i, new_index)

# Prints an error on the screen with a distinct text color of red.
def print_error(value, end="\n"):
    print(ansi.ansify(str(value)).fgcol(ansi.COLOR_RED).bold(), end=end)

def print_separator(c="*", count=20):
    print(c * count)