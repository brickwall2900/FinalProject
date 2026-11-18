def to_coordinate_numbers(real):
    ''' custom base-40 translator; base-10 -> base-40 '''
    REAL_TO_COORDINATE_VALUES = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                                "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
                                "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                                "u", "v", "w", "x", "y", "z", "@", "#", "$", "&"]
    if real >= len(REAL_TO_COORDINATE_VALUES) or real < 0:
        return "?"

    return REAL_TO_COORDINATE_VALUES[real]

def to_real_numbers(coordinate):
    ''' custom base-40 translator; base-40 -> base-10 '''
    REAL_TO_COORDINATE_VALUES = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                                "a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
                                "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                                "u", "v", "w", "x", "y", "z", "@", "#", "$", "&"]
    for real in range(len(REAL_TO_COORDINATE_VALUES)):
        if coordinate == REAL_TO_COORDINATE_VALUES[real]:
            return real

    return None