# Utility functions

# safeint() functions equivalently like int(), but returns `None` on invalid input.
def safeint(given, default=None):
    if str.isdigit(given):
        return int(given)
    else:
        return default