# common types of errors
# errors so my program does nOT crash ;-;

# i kinda took inspiration from Windows' Kernel32::GetLastError()
# or plainly just C

STATUS_SUCCESS                      = 0x0
STATUS_INDEX_OUT_OF_BOUNDS          = 0x1
STATUS_FILE_NOT_FOUND               = 0x2
STATUS_ALREADY_EXISTS               = 0x3
STATUS_UNDERPOPULATED               = 0x4

STATUS_CODE_TO_STRING_TABLE = {
    STATUS_SUCCESS: "The operation was successful.",
    STATUS_INDEX_OUT_OF_BOUNDS: "The operation was accessing a list with an index out-of-bounds.",
    STATUS_FILE_NOT_FOUND: "The operation requires a file %s that is not found on disk.",
    STATUS_ALREADY_EXISTS: "The operation expects the object to not exist, but it already exists.",
    STATUS_UNDERPOPULATED: "The operation expects a list to be populated by a certain size but did not meet that requirement.",
}

STATUS_CODE_TO_LITERAL_TABLE = {
    STATUS_SUCCESS: "STATUS_SUCCESS",
    STATUS_INDEX_OUT_OF_BOUNDS: "STATUS_INDEX_OUT_OF_BOUNDS",
    STATUS_FILE_NOT_FOUND: "STATUS_FILE_NOT_FOUND",
    STATUS_ALREADY_EXISTS: "STATUS_ALREADY_EXISTS",
    STATUS_UNDERPOPULATED: "STATUS_UNDERPOPULATED",
}