from logging import DEBUG

import ansi
import terminal
from common import safeint
from status import STATUS_SUCCESS, STATUS_OUT_OF_BOUNDS, STATUS_BAD_USER_INPUT, STATUS_PREVIOUS, STATUS_NEXT

# taken from exercise 5, 6, 7

INDEX_OPTION        = 0
INDEX_NAME          = 1
INDEX_FUNCTION      = 2

PDEBUG              = False

def print_ask_execute_procedures(header,
                                 separator_char,
                                 procedures,
                                 prompt="Enter a choice: ",
                                 status_footer=None,
                                 after_header=None,
                                 header_offset=0,
                                 procedure_offset=0,
                                 procedure_limit=10):
    if terminal.use_advanced_terminal_graphics:
        # terminal.erase_whole_screen()
        header_width = terminal.get_string_visual_width(header)
        max_width = max(40, header_width)
        border = "=" * max_width

        width = terminal.get_width()
        height = terminal.get_height()

        procedure_offset = max(0, min(len(procedures), procedure_offset))

        safe_height = height - 10
        _, after_header_lines = terminal.get_wrap_lines(after_header or "", max_width=max_width, word_wrap=True)
        _, status_footer_lines = terminal.get_wrap_lines(status_footer or "", max_width=max_width, word_wrap=True)
        procedure_y = 1 + 1 + 1 + after_header_lines
        procedure_visual_height = 1 + 1 + 1 + after_header_lines + max(min(len(procedures) + 2, safe_height, procedure_limit), 1) + 1 + status_footer_lines + 1 + 1
        # procedure_visual_height = border + header + separator + after_header + procedures + space + status_footer + prompt + border
        pos_x = width / 2 - max_width / 2
        pos_y = max(height / 2 - procedure_visual_height / 2, 1)

        show_more_option = pos_y + procedure_visual_height >= safe_height and len(procedures) >= procedure_limit
        if PDEBUG:
            print(pos_y + procedure_visual_height >= safe_height)
            print(pos_y + procedure_visual_height)
            print(safe_height)
            print(procedure_visual_height)
            print(procedure_offset)
            print(show_more_option)

        terminal.tgfx_print_text(border, pos_x, pos_y)
        terminal.tgfx_print_text(header, pos_x + (max_width / 2) - ((header_width + header_offset) / 2), pos_y + 1)
        terminal.tgfx_print_text((separator_char * max_width)[:max_width], pos_x, pos_y + 2)

        if after_header is not None:
            terminal.tgfx_print_text(after_header, pos_x, pos_y + 3, max_width=max_width, word_wrap=True)

        if len(procedures) == 0:
            print(ansi.bold("", persist=True), end="")
            terminal.tgfx_print_text("<none>", pos_x, procedure_y + pos_y)
            print(terminal.ESCAPE_RESET_GRAPHICS, end="")

        procedures_shown = 0
        for i in range(len(procedures)):
            if (show_more_option and i+pos_y >= safe_height) or procedures_shown >= procedure_limit:
                break
            if i + procedure_offset >= len(procedures) or i + procedure_offset < 0:
                break
            procedures_shown += 1
            procedure = procedures[i + procedure_offset]
            print(ansi.bold("", persist=True), end="")
            terminal.tgfx_print_text(f"[{str(procedure[INDEX_OPTION])}] {procedure[INDEX_NAME]}", pos_x, procedure_y + pos_y)
            print(terminal.ESCAPE_RESET_GRAPHICS, end="")
            procedure_y += 1

        if show_more_option:
            print(ansi.bold("", persist=True), end="")
            terminal.tgfx_print_text(f"[W] Next page...", pos_x,
                                     procedure_y + pos_y)
            terminal.tgfx_print_text(f"[Q] Prev page...", pos_x,
                                     procedure_y + pos_y + 1)
            print(terminal.ESCAPE_RESET_GRAPHICS, end="")
            procedure_y += 2

        if status_footer is not None:
            procedure_y += 1
            terminal.tgfx_print_text(status_footer, pos_x, pos_y + procedure_y, max_width=max_width,
                                     word_wrap=True)

        terminal.tgfx_print_text(border, pos_x, pos_y + status_footer_lines + procedure_y + 1)
        terminal.put_cursor_to(pos_x, pos_y + status_footer_lines + procedure_y)

        raw_option = input(prompt)
        option = safeint(raw_option)
        if terminal.use_advanced_terminal_graphics:
            terminal.tgfx_draw_rect(pos_x,
                                    pos_y,
                                    max_width,
                                    procedure_visual_height,
                                    char=" ",
                                    inner_char=" ")  # clear rect
            terminal.reset_cursor_to_top_left()

        if option is None:
            if raw_option.upper().endswith("Q") and procedure_offset - procedures_shown >= 0: # left arrow
                return STATUS_PREVIOUS, procedures_shown
            elif raw_option.upper().endswith("W") and procedure_offset + procedures_shown < len(procedures): # right arrow
                return STATUS_NEXT, procedures_shown

        status_code = do_execute_procedure(procedures, option)

        return status_code, option

        # return pos_x, pos_y, max_width, mpos_y - pos_y - 2 + max(1, len(procedures))
    else:
        if header is not None:
            print(f"{separator_char * 5} {header} {separator_char * 5}")

        if after_header is not None:
            print(after_header)
            print()

        if len(procedures) == 0:
            print("<none>")
            return STATUS_SUCCESS, 0 # FIXME: what to do?

        for procedure in procedures:
            print(f"[{str(procedure[INDEX_OPTION])}] {procedure[INDEX_NAME]}")

        option = safeint(input(prompt))
        print()
        if terminal.use_advanced_terminal_graphics:
            terminal.reset_cursor_to_top_left()
        return do_execute_procedure(procedures, option), option

# defines a procedure
def defproc(option, name, func):
    return [ option, name, func ]

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
            # TODO: allowed by lab instructor? tuples not allowed...
            procedure[INDEX_FUNCTION]()

        print()
        return STATUS_SUCCESS
    else:
        return STATUS_BAD_USER_INPUT