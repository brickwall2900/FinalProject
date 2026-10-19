# TODO: does my lab instructor allow this? NOT ALLOWED; put into not objects and classes

import os

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

def get_string_visual_width(text: str) -> int:
    width = 0
    for c in text:
        if c.isascii() and c.isprintable():
            width += 1

    return width

def get_wrap_lines(text, max_width=None, word_wrap=False):
    if max_width is None:
        max_width = 999999

    if max_width < 0:
        return STATUS_OUT_OF_BOUNDS, -1

    lines = 1
    str_pos = 0
    str_len = len(text)
    word_wrapped = False
    while str_pos < str_len:
        current_width = min(max_width, str_len)
        if word_wrap:
            word_wrapped = True
            while current_width + str_pos < str_len and not text[current_width + str_pos].isspace():
                current_width -= 1
        str_pos += current_width
        if word_wrapped:
            str_pos += 1
            word_wrapped = False
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

def tgfx_print_text(text: str, x, y, max_width=None, word_wrap=False):
    if max_width is None:
        max_width = 999999

    if max_width < 0:
        return STATUS_OUT_OF_BOUNDS

    pos_x = x
    pos_y = y
    str_pos = 0
    str_len = len(text)
    word_wrapped = False
    while str_pos < str_len:
        put_cursor_to(pos_x, pos_y)
        current_width = min(max_width, str_len)
        if word_wrap:
            word_wrapped = True
            while current_width+str_pos < str_len and not text[current_width+str_pos].isspace():
                current_width -= 1
        print(text[str_pos:current_width+str_pos], end="")
        str_pos += current_width
        if word_wrapped:
            str_pos += 1
            word_wrapped = False
        pos_y += 1

    return STATUS_SUCCESS


use_advanced_terminal_graphics = bool(os.environ.get("ADV_TERM_GFX", "True"))
use_advanced_terminal_graphics = use_advanced_terminal_graphics and get_width() >= 80 and get_height() >= 24