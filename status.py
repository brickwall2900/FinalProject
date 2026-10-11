# common types of errors
# errors so my program does nOT crash ;-;

# i kinda took inspiration from Windows' Kernel32::GetLastError()
# or plainly just C

STATUS_SUCCESS                      = 0x0
STATUS_INDEX_OUT_OF_BOUNDS          = 0x1
STATUS_FILE_NOT_FOUND               = 0x2
STATUS_ALREADY_EXISTS               = 0x3

def to_string(e):
    if e == STATUS_SUCCESS:
        return "The operation was successful"
    elif e == STATUS_INDEX_OUT_OF_BOUNDS:
        return "The operation was accessing a list with an index out-of-bounds."
    elif e == STATUS_FILE_NOT_FOUND:
        return "The operation requires a file %s that is not found on disk."
    elif e == STATUS_ALREADY_EXISTS:
        return "The operation expects the object to not exist, but it already exists."

    return "The operation.... did something."