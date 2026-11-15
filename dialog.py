import terminal
import procedures
import ansi

def alert(message,
          title="Dialog",
          options=["OK"],
          default_option="OK",
          prompt="Enter a choice: "):
    # we make a procedure list instead
    # all roads lead to the procedure system
    procedure_list = [] if options is not None else None

    if options is not None and procedure_list is not None:
        for i in range(len(options)):
            option = options[i]
            procedure_list.append(procedures.defproc(i, 
                                                    f"({option})" if default_option == option else option,
                                                    None))

    status_footer = None
    while True:
        _, option, _ = procedures.ask_procedure(title,
                                             "!",
                                             procedure_list,
                                             after_header=message,
                                             status_footer=status_footer,
                                             prompt=prompt)
        if procedure_list is not None and procedures.find_procedure(procedure_list, option):
            return options[option] if options is not None else True # wtf am is supposed to give!?
        else:
            return default_option

def input(message,
          title="Input",
          prompt="Enter: "):

    # okay tihs might just be stpid
    _, _, raw_option = procedures.ask_procedure(title,
                                                "!",
                                                None,
                                                after_header=message,
                                                prompt=prompt)
    return raw_option
    