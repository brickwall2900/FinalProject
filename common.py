import random


def safeint(given, default=None):
    
    '''
    safeint() functions equivalently like int(),
    but returns `default` on invalid input.
    '''
    
    if isinstance(given, str):
        is_negative = str.startswith(given, "-")
        if str.startswith(given, "-") or str.startswith(given, "+"):
            given = given[1:]
            
        if str.isdigit(given) and str.isascii(given):
            return int(given) * (-1 if is_negative else 1)
    return default

# NOTE: safefloat is deleted
# to emulate safe behavior, * 100 and turn it into an int.

def swap(the_list, a, b):
    '''
    Swaps two items in a list in-place.
    Users should check indices before swapping.
    '''
    
    tmp = the_list[a]
    the_list[a] = the_list[b]
    the_list[b] = tmp

def sort(the_list, comparator):
    ''' Sorts a given list using a given comparator function. '''
    
    for i in range(len(the_list)):
        min_value_idx = i
        for j in range(i + 1, len(the_list)):
            # this > that
            if comparator(the_list[min_value_idx], the_list[j]) > 0:
                min_value_idx = j
        swap(the_list, i, min_value_idx)

def find(haystack, needle):
    '''Performs linear search and returns an index of needle in list haystack.'''
    
    for i in range(len(haystack)):
        if haystack[i] == needle:
            return i

    return None

def randbool():
    ''' Generates a random boolean True or False. '''
    return random.randint(0, 1) == 1

def lerp(a, b, t):
    ''' Linear interpolation function. '''
    return a + (b - a) * t

def clamp(value, min_value, max_value):
    ''' Restricts value to range [min, max]. '''
    return min(max(value, min_value), max_value)

def str_to_bool(given):
    ''' Safely converts a string to a boolean. '''
    if given is None:
        return False

    if not isinstance(given, str):
        given = str(given)

    return given.strip().lower() == "true"
    
def yes_or_no(question):
    ''' Checks if the given string agrees with a question. '''
    
    given_text = input(question + "? (YES/NO) ")
    
    if str_to_bool(given_text):
        return True
        
    if not isinstance(given_text, str):
        return False
        
    return given_text.strip().lower().startswith("y")

def get_whole_digits(number):
    '''
    Returns the number of digits in a number.
    Does not consider decimal digits.
    '''
    if number == 0:
        return 0
    
    number = -number if number < 0 else number
    digit_count = 0
    while True:
        quotient = number // 10
        if quotient != 0:
            digit_count += 1
        else:
            break
        number = quotient
    return digit_count + 1

def print_error(value):
    ''' Prints an error on the screen. '''
    print(" !!! [ERROR] !!! ")
    print(value)
    print()
    pause()

def pause():
    ''' Pauses execution until the user presses Enter. '''
    print("Press [ENTER] to continue... ", end="")
    input()
    print()

