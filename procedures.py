from common import safeint

INDEX_OPTION        = 0
INDEX_NAME          = 1
INDEX_FUNCTION      = 2
INDEX_ARGS_TUPLE    = 3

# taken from exercise 5
def print_procedures(header, separator_char, procedures, after_header=None):
    if header is not None:
        print(f"{separator_char * 5} {header} {separator_char * 5}")

    if after_header is not None:
        print(after_header)
        print()

    if len(procedures) == 0:
        print("<none>")
        return

    for procedure in procedures:
        print(f"{str(procedure[INDEX_OPTION])}. {procedure[INDEX_NAME]}")

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
            return False

        if procedure[INDEX_FUNCTION] is not None:
            # TODO: allowed by lab instructor?
            procedure[INDEX_FUNCTION](*procedure[INDEX_ARGS_TUPLE])

        print()
        return True
    else:
        return False

# asks the user for an option in the menu then executes it
def ask_and_execute_procedure(procedures, prompt="Enter a choice: "):
    option = safeint(input(prompt))
    print()
    return do_execute_procedure(procedures, option), option