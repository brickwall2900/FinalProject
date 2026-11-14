# simple fucking property-like parser
# key=value

# on everything i finish this project on time lol

from status import *

# input (str) -> dict[key]: value
def deserialize(input):
    if input is None:
        return STATUS_NULL_POINTER, None

    # TODO: autocompletion, remove!
    input = str(input)
    parsed = {}

    for line in input.splitlines():
        equals_index = line.find("=")
        if equals_index == -1:
            return STATUS_BAD_USER_INPUT, None

        key = line[:equals_index - 1]
        value = line[equals_index:]
        parsed[key] = value

    return STATUS_SUCCESS, parsed

# input (dict[key]: value) -> str
def serialize(data):
    # isinstance checks if the instance of `data` is of a given class
    if not isinstance(data, dict): # checks if data is a dict
        return STATUS_BAD_USER_INPUT, None

    serialized = ""
    for key, value in enumerate(data):
        serialized = f"{key}={value}\n"

    return STATUS_SUCCESS, serialized