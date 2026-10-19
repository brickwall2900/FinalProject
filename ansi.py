from terminal import ESCAPE_SEQUENCE

# https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797

BOLD                = ESCAPE_SEQUENCE + "1m"
UNBOLD              = ESCAPE_SEQUENCE + "22n"
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