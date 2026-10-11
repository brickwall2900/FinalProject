from common import safeint

INDEX_OPTION        = 0
INDEX_NAME          = 1
INDEX_FUNCTION      = 2

# taken from exercise 5
def print_procedures(header, separator_char, procedures):
    if header is not None:
        print(f"{separator_char * 5} {header} {separator_char * 5}")

    # I used a custom "procedure" system
    # where each procedure is stored in a list
    # and its value is another list containing
    # the option number, procedure name, and function to call.

    # it is really useful since it allows for easy implementation of functions
    # and choices like this one so I don't have to check against an if-statement
    # each time I implement a new choice.
    if len(procedures) == 0:
        print("<none>")
        return

    for procedure in procedures:
        print(f"{str(procedure[INDEX_OPTION])}. {procedure[INDEX_NAME]}")

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
            return False

        if procedure[INDEX_FUNCTION] is not None:
            procedure[INDEX_FUNCTION]()

        print()
        return True
    else:
        return False

# asks the user for an option in the menu then executes it
def ask_and_execute_procedure(procedures, prompt="Enter a choice: "):
    option = safeint(input(prompt))
    print()
    return do_execute_procedure(procedures, option), option