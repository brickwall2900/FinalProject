# TODO: does my lab instructor allow this?

ESCAPE_CHARACTER = "\u001b"
ESCAPE_SEQUENCE = ESCAPE_CHARACTER + "["
ESCAPE_RESET_GRAPHICS = ESCAPE_SEQUENCE + "0m"

FLAG_BG_COLORED         = 1 << 0
FLAG_FG_COLORED         = 1 << 1
FLAG_BOLD               = 1 << 2
FLAG_DIM                = 1 << 3
FLAG_ITALIC             = 1 << 4
FLAG_UNDERLINE          = 1 << 5
FLAG_BLINKING           = 1 << 6
FLAG_STRIKETHROUGH      = 1 << 7

COLOR_BLACK             = 0
COLOR_RED               = 1
COLOR_GREEN             = 2
COLOR_YELLOW            = 3
COLOR_BLUE              = 4
COLOR_MAGENTA           = 5
COLOR_CYAN              = 6
COLOR_WHITE             = 7
COLOR_DEFAULT           = 9

class AnsiBuilder:
    __flags = 0
    __fg_color = COLOR_DEFAULT
    __bg_color = COLOR_DEFAULT

    def __init__(self, contents):
        self.contents = contents

    def set_flag(self, which):
        self.__flags = self.__flags | which

    def clear_flag(self, which):
        self.__flags = self.__flags & ~which

    def has_flag(self, which):
        return (self.__flags & which) == which

    def toggle_flag(self, which, toggle):
        if toggle:
            self.set_flag(which)
        else:
            self.clear_flag(which)

    def bold(self):
        self.set_flag(FLAG_BOLD)
        return self

    def underline(self):
        self.set_flag(FLAG_UNDERLINE)
        return self

    def fgcol(self, color):
        self.set_flag(FLAG_FG_COLORED)
        self.__fg_color = color
        return self

    def bgcol(self, color):
        self.set_flag(FLAG_BG_COLORED)
        self.__bg_color = color
        return self

    def __compute_graphic_controls(self):
        result = []
        if self.has_flag(FLAG_BOLD):
            result.append("1m")

        if self.has_flag(FLAG_UNDERLINE):
            result.append("4m")

        if self.has_flag(FLAG_FG_COLORED):
            result.append(f"{30 + self.__fg_color}m")

        if self.has_flag(FLAG_BG_COLORED):
            result.append(f"{40 + self.__bg_color}m")

        return "".join([ESCAPE_SEQUENCE + x for x in result])

    def __str__(self) -> str:
        return (self.__compute_graphic_controls()
                + self.contents
                + ESCAPE_RESET_GRAPHICS)

def ansify(contents):
    return AnsiBuilder(contents)