from terminal import ESCAPE_SEQUENCE, ESCAPE_CHARACTER

# https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797

BOLD                = ESCAPE_SEQUENCE + "1m"
UNBOLD              = ESCAPE_SEQUENCE + "22m"
ITALIC              = ESCAPE_SEQUENCE + "3m"
UNITALIC            = ESCAPE_SEQUENCE + "23m"
UNDERLINE           = ESCAPE_SEQUENCE + "4m"
UNUNDERLINE         = ESCAPE_SEQUENCE + "24m"
UNFG_COLOR          = ESCAPE_SEQUENCE + "39m"
UNBG_COLOR          = ESCAPE_SEQUENCE + "49m"

def bold(str, apply=True, persist=False):
    return (BOLD if apply else "") + str + (UNBOLD if not persist else "")

def italic(str, apply=True, persist=False):
    return (ITALIC if apply else "") + str + (UNITALIC if not persist else "")

def underline(str, apply=True, persist=False):
    return (UNDERLINE if apply else "") + str + (UNUNDERLINE if not persist else "")

def fgcolor(str, color, apply=True, persist=False):
    return (f"{ESCAPE_SEQUENCE}{30 + color}m" if apply else "") + str + (UNFG_COLOR if not persist else "")

def bgcolor(str, color, apply=True, persist=False):
    return (f"{ESCAPE_SEQUENCE}{40 + color}m" if apply else "") + str + (UNBG_COLOR if not persist else "")

def get_raw_string(text_with_ansi):
    raw = ""
    index = 0
    length = len(text_with_ansi)
    in_escape_sequence = False
    while index < length:
        char = text_with_ansi[index]

        if in_escape_sequence:
            if char == "m":
                in_escape_sequence = False
        else:
            is_escape_sequence = char == ESCAPE_CHARACTER
            if is_escape_sequence:
                in_escape_sequence = True
            else:
                raw += char
        index += 1
    return raw

def to_ansi_tokens(text_with_ansi):
    tokens = []
    buffer = ""
    index = 0
    length = len(text_with_ansi)
    in_escape_sequence = False
    while index < length:
        char = text_with_ansi[index]

        if in_escape_sequence:
            if char == "m":
                in_escape_sequence = False
                tokens.append(buffer + "m")
                buffer = ""
            else:
                buffer += char
        else:
            is_escape_sequence = char == ESCAPE_CHARACTER
            if is_escape_sequence:
                in_escape_sequence = True
                if len(buffer) > 0:
                    tokens.append(buffer)
                buffer = ESCAPE_CHARACTER
            else:
                buffer += char
        index += 1

    if len(buffer) > 0:
        tokens.append(buffer)
    
    return tokens

def is_ansi_token(token):
    return token is not None and str(token).startswith(ESCAPE_SEQUENCE)