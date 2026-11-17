import os

from status import STATUS_SUCCESS, STATUS_OUT_OF_BOUNDS, STATUS_NULL_POINTER

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
    print(ESCAPE_SEQUENCE + "2J", end="")

def put_cursor_to(x, y):
    print(ESCAPE_SEQUENCE + f"{int(y)};{int(x)}H", end="")

def reset_graphics():
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

    lines = 0
    for paragraph in text.splitlines():
        if max_width is None:
            lines = 1
        elif word_wrap:
            import ansi
            tokens = ansi.to_ansi_tokens(paragraph)

            for token in tokens:
                if not ansi.is_ansi_token(token):
                    str_pos = 0
                    while str_pos < len(token):
                        if len(token) - str_pos <= max_width:
                            lines += 1
                            break
        
                        space_idx = token.rfind(" ", str_pos, str_pos + max_width + 1)
                        if space_idx > str_pos:
                            lines += 1
                            str_pos = space_idx + 1
                        else: # case where one word exceeds max_width, just split it
                            lines += 1
                            str_pos += max_width
        else:
            lines = len([paragraph[i:i + max_width] for i in range(0, len(paragraph), max_width)]) or 1

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

    x = int(x)
    y = int(y)
    max_width = int(max_width)

    pos_x = x
    pos_y = y
    
    for paragraph in text.splitlines():
        if max_width is None:
            lines = [paragraph]
        elif word_wrap:
            import ansi
            lines = []
            tokens = ansi.to_ansi_tokens(paragraph)
            line_buffer = ""

            for token in tokens:
                if ansi.is_ansi_token(token):
                    line_buffer += token
                else:
                    str_pos = 0
                    while str_pos < len(token):
                        if len(token) - str_pos <= max_width:
                            lines.append(line_buffer + token[str_pos:])
                            line_buffer = ""
                            break
        
                        space_idx = token.rfind(" ", str_pos, str_pos + max_width + 1)
                        if space_idx > str_pos:
                            lines.append(line_buffer + token[str_pos:space_idx])
                            str_pos = space_idx + 1
                        else: # case where one word exceeds max_width, just split it
                            lines.append(line_buffer + token[str_pos:str_pos + max_width])
                            str_pos += max_width
                        line_buffer = ""

            if len(line_buffer) > 0:
                lines[-1] = lines[-1] + line_buffer
        else:
            lines = [paragraph[i:i + max_width] for i in range(0, len(paragraph), max_width)] or [""]

        for line in lines:
            put_cursor_to(pos_x, pos_y)
            print(line, end="")
            pos_y += 1

    return STATUS_SUCCESS

def tgfx_warn_no_space(required_width, required_height=None):
    has_screen_space_estate = int(required_width) < get_width() - 1
    if required_height is not None:
        has_screen_space_estate = has_screen_space_estate and int(required_height) < get_height() - 1

    if not has_screen_space_estate:
        import ansi
        erase_whole_screen()
        tgfx_print_text(ansi.bgcolor(ansi.fgcolor("Your terminal does not have more screen space" \
        " estate to draw the elements on screen correctly. Please resize the terminal " \
        "and refresh the screen buffer.", COLOR_WHITE), COLOR_RED), 0, 0)

    return has_screen_space_estate

# Converts a string to a boolean
# put here cuz importing common would cause a circular dependency
def str_to_bool(given):
    if given is None:
        return False

    if not isinstance(given, str):
        return False

    return given.strip().lower() == "true"

use_advanced_terminal_graphics = str_to_bool(os.environ.get("ADV_TERM_GFX", "True")) and True
# use_advanced_terminal_graphics = use_advanced_terminal_graphics and get_width() >= 80 and get_height() >= 24
