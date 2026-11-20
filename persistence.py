import parser
import os

def load_persistence(name):
    '''
    Loads a persistance file (located at ./persistence/&lt;name&gt;.properties) and parses it.
    Returns a dict if successful, None if the parsed Python dictionary failed to deserialize.
    '''
    
    # ./persistence
    persistence_folder = os.path.join("persistence")
    
    # check if persistence folder exists
    # if it does not exist, create it as a folder
    if not os.path.exists(persistence_folder):
        os.mkdir(persistence_folder)

    # joins paths together (persistence_folder + "/" + name.properties)
    # ./persistence/<name>.properties
    path = os.path.join(persistence_folder, name + ".properties")

    if os.path.exists(path):
        with open(path, "r") as file:
            # read the file as whole string
            serialized = file.read()
            return parser.deserialize(serialized)
    else:
        return None

# returns True if successful
def save_persistence(name, data):
    '''
    Saves a persistance file (located at ./persistence/&lt;name&gt;.properties)
    Returns True if successful, False if the Python dictionary failed to parse.
    '''
    
    persistence_folder = os.path.join("persistence")
    
    if not os.path.exists(persistence_folder):
        os.mkdir(persistence_folder)

    path = os.path.join(persistence_folder, name + ".properties")

    # open(path, "x") creates an empty file and if the file already exists, don't error out
    if os.path.exists(path):
        with open(path, "a") as file:
            pass

    with open(path, "w") as file:
        serialized = parser.serialize(data)
        if serialized is not None:
            file.write(serialized)
            return True
        else:
            return False

# returns true if successful
def remove_persistence(name):
    ''' Removes a persistance file (located at ./persistence/&lt;name&gt;.properties) if exists '''
        
    persistence_folder = os.path.join("persistence")
    if not os.path.exists(persistence_folder):
        return

    path = os.path.join(persistence_folder, (name + ".properties"))

    if os.path.exists(path):
        os.remove(path)
