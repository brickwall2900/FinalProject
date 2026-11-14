import terminal
import procedures
import ansi

def alert(message,
          title="Dialog",
          options=["OK"],
          default_option="OK"):
    # we make a procedure list instead
    # all roads lead to the procedure system
    procedure_list = []
    for i in range(len(options)):
        option = options[i]
        procedure_list.append(procedures.defproc(i, 
                                                 ansi.bgcolor(ansi.fgcolor(option, terminal.COLOR_BLACK), terminal.COLOR_WHITE) if default_option == option else option,
                                                 None))

    _, option = None, None
    status_footer = None
    while True:
        _, option = procedures.ask_procedure(title,
                                             "!",
                                             procedure_list,
                                             after_header=message,
                                             status_footer=status_footer)
        if procedures.find_procedure(procedure_list, option):
            return options[option]
        else:
            return default_option
        