# simple fucking property-like parser
# key=value

# on everything i finish this project on time lol

# input (str) -> dict[key, value]
def deserialize(serialized):
    if serialized is None:
        return None

    parsed = {}
    for line in serialized.splitlines():
        equals_index = line.find("=")
        # skip if = not found
        if equals_index == -1:
            return None

        key = line[:equals_index]
        value = line[equals_index+1:]
        parsed[key] = value

    return parsed

# input (dict[key]: value) -> str
def serialize(data):
    
    # TODO: do we need this?
    # isinstance checks if the instance of `data` is of a given class
    if not isinstance(data, dict): # checks if data is a dict
        return None

    serialized = ""
    for key in data.keys():
        serialized = serialized + f"{key}={data[key]}\n"

    return serialized
