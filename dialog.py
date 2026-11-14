import terminal
import procedures

def alert(message,
          title="Dialog",
          options=["OK"]):
    # we make a procedure list instead
    # all roads lead to the procedure system
    procedure_list = []
    for i in range(len(options)):
        option = options[i]
        procedure_list.append(procedures.defproc(i, option, None))

    _, option = None, None
    while option is None:
        _, option = procedures.ask_procedure(title,
                                             "!",
                                             procedure_list,
                                             after_header=message)

    return option