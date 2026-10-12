import terminal
from common import safeint
from status import STATUS_SUCCESS, STATUS_OUT_OF_BOUNDS, STATUS_BAD_USER_INPUT

# taken from exercise 5, 6, 7

INDEX_OPTION        = 0
INDEX_NAME          = 1
INDEX_FUNCTION      = 2
INDEX_ARGS_TUPLE    = 3

def print_procedures(header, separator_char, procedures, before_header=None, after_header=None):
    if terminal.use_advanced_terminal_graphics:
        terminal.erase_whole_screen()
        header_width = terminal.get_string_visual_width(header)
        max_width = max(40, header_width)
        border = "=" * max_width

        width = terminal.get_width()
        height = terminal.get_height()
        pos_x = width / 2 - max_width / 2
        pos_y = height / 2
        _, after_header_lines = terminal.get_wrap_lines(after_header or "", max_width=max_width, word_wrap=True)
        _, before_header_lines = terminal.get_wrap_lines(before_header or "", max_width=max_width, word_wrap=True)
        mpos_y = pos_y + 2 + after_header_lines

        pos_y += before_header_lines

        # terminal.tgfx_draw_rect(pos_x, pos_y, max_width, mpos_y - pos_y - 2 + len(procedures), char=" ") # clear rect
        if before_header is not None:
            terminal.tgfx_print_text(before_header, pos_x, pos_y - before_header_lines, max_width=max_width, word_wrap=True)

        terminal.tgfx_print_text(border, pos_x, pos_y - 1)
        terminal.tgfx_print_text(header, pos_x + (max_width / 2) - (header_width / 2), pos_y)
        terminal.tgfx_print_text((separator_char * max_width)[:max_width], pos_x, pos_y + 1)

        if after_header is not None:
            terminal.tgfx_print_text(after_header, pos_x, pos_y + 2, max_width=max_width, word_wrap=True)

        if len(procedures) == 0:
            print(terminal.ansify().bold().persist(), end="")
            terminal.tgfx_print_text("<none>", pos_x, mpos_y)
            print(terminal.ESCAPE_RESET_GRAPHICS, end="")

        for procedure in procedures:
            print(terminal.ansify().bold().persist(), end="")
            terminal.tgfx_print_text(f"[{str(procedure[INDEX_OPTION])}] {procedure[INDEX_NAME]}", pos_x, mpos_y)
            print(terminal.ESCAPE_RESET_GRAPHICS, end="")
            mpos_y += 1

        terminal.tgfx_print_text(border, pos_x, mpos_y + 2)
        terminal.put_cursor_to(pos_x, mpos_y + 1)
    else:
        if header is not None:
            print(f"{separator_char * 5} {header} {separator_char * 5}")

        if after_header is not None:
            print(after_header)
            print()

        if len(procedures) == 0:
            print("<none>")
            return

        for procedure in procedures:
            print(f"[{str(procedure[INDEX_OPTION])}] {procedure[INDEX_NAME]}")

# defines a procedure
def defproc(option, name, func, *args):
    return [ option, name, func, args ]

# finds a procedure corresponding to a given choice
def find_procedure(procedures, choice):
    for procedure in procedures:
        if procedure[INDEX_OPTION] == choice:
            return procedure
    return None

# attempts executing the procedure
def do_execute_procedure(procedures, choice):
    if choice is not None:
        procedure = find_procedure(procedures, choice)

        if procedure is None:
            return STATUS_OUT_OF_BOUNDS

        if procedure[INDEX_FUNCTION] is not None:
            # TODO: allowed by lab instructor?
            procedure[INDEX_FUNCTION](*procedure[INDEX_ARGS_TUPLE])

        print()
        return STATUS_SUCCESS
    else:
        return STATUS_BAD_USER_INPUT

# asks the user for an option in the menu then executes it
def ask_and_execute_procedure(procedures, prompt="Enter a choice: "):
    option = safeint(input(prompt))
    print()
    if terminal.use_advanced_terminal_graphics:
        terminal.reset_cursor_to_top_left()
    return do_execute_procedure(procedures, option), option