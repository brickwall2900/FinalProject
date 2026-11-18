import random

# safeint() functions equivalently like int(), but returns `None` on invalid input.
def safeint(given, default=None):
    if str.isdigit(given) and str.isascii(given):
        return int(given)
    else:
        return default

# NOTE: safefloat is deleted
# to emulate safe behavior, * 100 and turn it into an int.

# Swaps two items in a list in-place.
# APINOTE: user should check indices before swapping.
def swap(the_list, a, b):
    tmp = the_list[a]
    the_list[a] = the_list[b]
    the_list[b] = tmp

# Sorts a given list using a given comparator function
# selection sort, please change to something more "performative"
# selection sort is the most simplest thing i've thought of and i have no sleep
def sort(the_list, comparator):
    for i in range(len(the_list)):
        min_value_idx = i
        for j in range(i + 1, len(the_list)):
            if comparator(the_list[min_value_idx], the_list[j]) > 0: # this > that
                min_value_idx = j
        swap(the_list, i, min_value_idx)

# Linear search
def find(haystack, needle):
    for i in range(len(haystack)):
        if haystack[i] == needle:
            return i

    return None

# Generates a random boolean True or False
def randbool():
    return random.randint(0, 1) == 1

# linear interpolation
def lerp(a, b, t):
    return a + (b - a) * t

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

# Prints an error on the screen with a distinct text color of red.
def print_error(value):
    print(" !!! ERROR !!! ")
    print(value)
    print()
    print("Press [ENTER] to continue... ", end="")
    input()