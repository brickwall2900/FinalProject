# Utility functions
import ansi


# safeint() functions equivalently like int(), but returns `None` on invalid input.
def safeint(given, default=None):
    if str.isdigit(given):
        return int(given)
    else:
        return default

def print_error(value, end="\n"):
    print(ansi.ansify(str(value)).fgcol(ansi.COLOR_RED).bold(), end=end)