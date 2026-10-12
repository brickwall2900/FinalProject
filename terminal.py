# TODO: does my lab instructor allow this?

import os
import math

from status import STATUS_SUCCESS, STATUS_OUT_OF_BOUNDS

ESCAPE_CHARACTER = "\u001b"
ESCAPE_SEQUENCE = ESCAPE_CHARACTER + "["
ESCAPE_RESET_GRAPHICS = ESCAPE_SEQUENCE + "0m"

DEFAULT_WIDTH           = 80
DEFAULT_HEIGHT          = 24

FLAG_BG_COLORED         = 1 << 0
FLAG_FG_COLORED         = 1 << 1
FLAG_BOLD               = 1 << 2
FLAG_DIM                = 1 << 3
FLAG_ITALIC             = 1 << 4
FLAG_UNDERLINE          = 1 << 5
FLAG_BLINKING           = 1 << 6
FLAG_STRIKETHROUGH      = 1 << 7
FLAG_NOT_RESETS         = 1 << 8

COLOR_BLACK             = 0
COLOR_RED               = 1
COLOR_GREEN             = 2
COLOR_YELLOW            = 3
COLOR_BLUE              = 4
COLOR_MAGENTA           = 5
COLOR_CYAN              = 6
COLOR_WHITE             = 7
COLOR_DEFAULT           = 9

use_advanced_terminal_graphics = bool(os.environ.get("ADV_TERM_GFX", "True"))

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

    def persist(self):
        self.set_flag(FLAG_NOT_RESETS)
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
                + ("" if self.has_flag(FLAG_NOT_RESETS) else ESCAPE_RESET_GRAPHICS)) \
            if use_advanced_terminal_graphics else self.contents

def ansify(contents = None):
    return AnsiBuilder(contents if contents is not None else "")

def reset_cursor_to_top_left():
    if not use_advanced_terminal_graphics:
        return
    print(ESCAPE_SEQUENCE + "H", end="")

def erase_whole_screen():
    if not use_advanced_terminal_graphics:
        return
    print(ESCAPE_SEQUENCE + "2J", end="")

def put_cursor_to(x, y):
    if not use_advanced_terminal_graphics:
        return
    print(ESCAPE_SEQUENCE + f"{int(y)};{int(x)}H", end="")

def reset_graphics():
    if not use_advanced_terminal_graphics:
        return
    print(ESCAPE_RESET_GRAPHICS, end="")

def flush():
    print("", end="", flush=True)

def get_width():
    if os.isatty(1):
        size = os.get_terminal_size(1)
        return size.columns
    else:
        return DEFAULT_WIDTH

def get_height():
    if os.isatty(1):
        size = os.get_terminal_size(1)
        return size.lines
    else:
        return DEFAULT_HEIGHT

def get_string_visual_width(text: str):
    width = 0
    for c in text:
        if c.isascii() and c.isprintable():
            width += 1

    return width

def get_wrap_lines(text, max_width=None):
    if max_width is None:
        max_width = 999999

    if max_width < 0:
        return STATUS_OUT_OF_BOUNDS, -1

    str_pos = 0
    str_len = len(text)
    lines = 1
    while str_pos < str_len:
        current_width = min(max_width, str_len)
        str_pos += current_width
        lines += 1

    return STATUS_SUCCESS, lines

def tgfx_draw_rect(x, y, width, height, char = "#", inner_char = " "):
    if width < 0 or height < 0:
        return STATUS_OUT_OF_BOUNDS

    x = int(x)
    y = int(y)
    width = int(width)
    height = int(height)

    for i in range(y, y + height):
        for j in range(x, x + width):
            put_cursor_to(j, i) # sorry WHAHAHAHAHAHAHAH
            print(char if j <= x or j >= (x+(width - 1)) or i <= y or i >= (y+(height - 1)) else inner_char, end="")
        print()

    return STATUS_SUCCESS

def tgfx_print_text(text, x, y, max_width=None):
    if max_width is None:
        max_width = 999999

    if max_width < 0:
        return STATUS_OUT_OF_BOUNDS

    pos_x = x
    pos_y = y
    str_pos = 0
    str_len = len(text)
    while str_pos < str_len:
        put_cursor_to(pos_x, pos_y)
        current_width = min(max_width, str_len)
        print(text[str_pos:current_width+str_pos], end="")
        str_pos += current_width
        pos_y += 1

    return STATUS_SUCCESS