import parser
import os

def load_persistence(name):
    persistence_folder = os.path.join("persistence")
    
    if not os.path.exists(persistence_folder):
        os.mkdir(persistence_folder)

    path = os.path.join(persistence_folder, name + ".properties")

    if os.path.exists(path):
        with open(path, "r") as file:
            serialized = file.read()
            return parser.deserialize(serialized)
    else:
        return None

# returns True if successful
def save_persistence(name, data):
    persistence_folder = os.path.join("persistence")
    
    if not os.path.exists(persistence_folder):
        os.mkdir(persistence_folder)

    path = os.path.join(persistence_folder, name + ".properties")

    # open(path, "x") creates an empty file if doesn't exist and writes to it
    with open(path, "x") as file:
        serialized = parser.serialize(data)
        if serialized is not None:
            file.write(serialized)
            return True
        else:
            return False

# returns true if successful
def remove_persistence(name):
    persistence_folder = os.path.join("persistence")
    if not os.path.exists(persistence_folder):
        return

    path = os.path.join(persistence_folder, (name + ".properties"))

    if os.path.exists(path):
        os.remove(path)
