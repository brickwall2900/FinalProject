from logging import DEBUG

import ansi
import terminal
from common import safeint, clamp
from status import STATUS_SUCCESS, STATUS_OUT_OF_BOUNDS, STATUS_BAD_USER_INPUT, STATUS_PREVIOUS, STATUS_NEXT

# taken from exercise 5, 6, 7

INDEX_OPTION        = 0
INDEX_NAME          = 1
INDEX_FUNCTION      = 2

# dispatch mechanism ;-;

def __ask_procedure_basic(header,
                          separator_char,
                          procedures,
                          prompt,
                          after_header,
                          status_footer,
                          procedure_offset,
                          procedure_limit,
                          text_effects):
    procedure_count = len(procedures)
    procedure_offset = clamp(procedure_offset, 0, procedure_count)
    page_size = max(1, procedure_limit)
    
    if header is not None:
        print(f"{separator_char * 5} {header} {separator_char * 5}")

    if after_header is not None:
        print(after_header)
        print()

    if procedure_count == 0:
        print("<none>")
        return STATUS_SUCCESS, 0 # FIXME: what to do?

    # calculate page
    visible_procedures = procedures[procedure_offset:procedure_offset + page_size]
    has_prev = procedure_offset > 0
    has_next = (procedure_offset + page_size) < procedure_count
    show_pagination = has_prev or has_next

    for procedure in visible_procedures:
        print(f"[{str(procedure[INDEX_OPTION])}] {procedure[INDEX_NAME]}")

    if show_pagination:
        print()
    if has_next:
        print("[W] Next page...")
    if has_prev:
        print("[Q] Prev page...")

    if status_footer is not None:
            print(after_header)
            print()

    raw_option = input(prompt)
    option = safeint(raw_option)

    if option is None:
        if raw_option.upper().endswith("Q") and has_prev: # left arrow
            return STATUS_PREVIOUS, page_size
        elif raw_option.upper().endswith("W") and has_next: # right arrow
            return STATUS_NEXT, page_size
    
    print()
    return STATUS_SUCCESS, option

def __ask_procedure_fancy(header,
                          separator_char,
                          procedures,
                          prompt,
                          after_header,
                          status_footer,
                          procedure_offset,
                          procedure_limit,
                          text_effects):
    terminal.erase_whole_screen()
    header_width = len(ansi.get_raw_string(header))
    max_width = max(40, header_width)
    border = "=" * max_width

    width = terminal.get_width()
    height = terminal.get_height()

    procedure_count = len(procedures)
    procedure_offset = clamp(procedure_offset, 0, procedure_count)

    # i swear to the almighty being that i wrote this on hand 
    safe_height = max(10, height - 10)
    _, after_header_line_count = terminal.get_wrap_lines(after_header or "", max_width=max_width, word_wrap=True)
    _, status_footer_line_count = terminal.get_wrap_lines(status_footer or "", max_width=max_width, word_wrap=True)
    footer_border_lines = (1 + status_footer_line_count) if status_footer is not None else 0

    # 5 because top border + separator + prompt + bottom border + empty spaces
    # 3 for pagination options (next, prev, empty space)
    available_for_items = max(1, safe_height - 5 - after_header_line_count - footer_border_lines - 3)
    page_size = max(1, min(procedure_limit, available_for_items))
    page_size = max(1, procedure_limit)

    visible_procedures = procedures[procedure_offset:procedure_offset + page_size]
    has_prev = procedure_offset > 0
    has_next = (procedure_offset + page_size) < procedure_count
    show_pagination = has_prev or has_next

    list_lines = max(1, len(visible_procedures)) + (3 if show_pagination else 0)
    box_height = 5 + after_header_line_count + list_lines + footer_border_lines
    
    pos_x = width / 2 - max_width / 2
    pos_y = max(height / 2 - box_height / 2, 1)

    terminal.tgfx_print_text(border, pos_x, pos_y)
    terminal.tgfx_print_text(header, pos_x + (max_width / 2) - ((header_width) / 2), pos_y + 1)
    terminal.tgfx_print_text((separator_char * max_width)[:max_width], pos_x, pos_y + 2)

    procedure_y = pos_y + 3

    if after_header is not None:
        terminal.tgfx_print_text(after_header, pos_x, pos_y + 3, max_width=max_width, word_wrap=True)

    procedure_y += after_header_line_count

    if procedure_count == 0:
        print(ansi.bold("", persist=True), end="")
        terminal.tgfx_print_text("<none>", pos_x, procedure_y)
        procedure_y += 1
        print(terminal.ESCAPE_RESET_GRAPHICS, end="")

    for procedure in visible_procedures:
        print(ansi.bold("", persist=True), end="")
        terminal.tgfx_print_text(f"[{str(procedure[INDEX_OPTION])}] {procedure[INDEX_NAME]}", pos_x, procedure_y)
        print(terminal.ESCAPE_RESET_GRAPHICS, end="")
        procedure_y += 1

    if show_pagination:
        print(ansi.bold("", persist=True), end="")
        procedure_y += 1
        if has_next:
            terminal.tgfx_print_text(f"[W] Next page...", pos_x,
                                        procedure_y)
            procedure_y += 1
        if has_prev:
            terminal.tgfx_print_text(f"[Q] Prev page...", pos_x,
                                        procedure_y)
            procedure_y += 1
        print(terminal.ESCAPE_RESET_GRAPHICS, end="")

    print()
    procedure_y += 1

    if status_footer is not None:
        terminal.tgfx_print_text(status_footer, pos_x, procedure_y, max_width=max_width,
                                    word_wrap=True)
        procedure_y += status_footer_line_count

    terminal.tgfx_print_text(border, pos_x, procedure_y + 1)
    terminal.put_cursor_to(pos_x, procedure_y)

    raw_option = input(prompt)
    option = safeint(raw_option)
    terminal.tgfx_draw_rect(pos_x,
                            pos_y,
                            max_width,
                            box_height,
                            char=" ",
                            inner_char=" ")  # clear rect

    if option is None:
        if raw_option.upper().endswith("Q") and has_prev: # left arrow
            return STATUS_PREVIOUS, page_size
        elif raw_option.upper().endswith("W") and has_next: # right arrow
            return STATUS_NEXT, page_size

    return STATUS_SUCCESS, option

    # return pos_x, pos_y, max_width, mpos_y - pos_y - 2 + max(1, len(procedures))

def ask_procedure(header,
                  separator_char,
                  procedures,
                  prompt="Enter a choice: ",
                  status_footer=None,
                  after_header=None,
                  procedure_offset=0,
                  procedure_limit=10,
                  text_effects=0):
    if terminal.use_advanced_terminal_graphics:
        return __ask_procedure_fancy(header, separator_char, procedures, prompt, after_header, status_footer, procedure_offset, procedure_limit, text_effects)
    else:
        return __ask_procedure_basic(header, separator_char, procedures, prompt, after_header, status_footer, procedure_offset, procedure_limit, text_effects)

# defines a procedure
def defproc(option, name, func):
    return [ option, name, func ]

# finds a procedure corresponding to a given choice
# linear search
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
            procedure[INDEX_FUNCTION]()

        print()
        return STATUS_SUCCESS
    else:
        return STATUS_BAD_USER_INPUT