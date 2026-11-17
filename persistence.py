import parser
from status import *
import os

PERSISTENCE_FOLDER = os.path.join("persistence")

def ensure_persistence_dir_exists():
    if os.path.exists(PERSISTENCE_FOLDER):
        if not os.path.isdir(PERSISTENCE_FOLDER):
            return False
        else:
            return True
    else:
        os.mkdir(PERSISTENCE_FOLDER)

    return True

def load_persistence(name):
    has_persistence_dir = ensure_persistence_dir_exists()
    if not has_persistence_dir:
        return STATUS_ALREADY_EXISTS, None

    path = os.path.join(PERSISTENCE_FOLDER, (name + ".properties"))

    if os.path.exists(path):
        with open(path, "r") as file:
            serialized = file.read()
            return parser.deserialize(serialized)
    else:
        return STATUS_FILE_NOT_FOUND, None

def save_persistence(name, data):
    has_persistence_dir = ensure_persistence_dir_exists()
    if not has_persistence_dir:
        return STATUS_ALREADY_EXISTS

    path = os.path.join(PERSISTENCE_FOLDER, (name + ".properties"))

    if not os.path.exists(path):
        with open(path, "a") as _:
            pass

    with open(path, "w") as file:
        status_code, serialized = parser.serialize(data)
        if status_code == STATUS_SUCCESS and serialized is not None:
            file.write(serialized)
            return STATUS_SUCCESS
        else:
            return status_code

def remove_persistence(name):
    has_persistence_dir = ensure_persistence_dir_exists()
    if not has_persistence_dir:
        return STATUS_ALREADY_EXISTS

    path = os.path.join(PERSISTENCE_FOLDER, (name + ".properties"))

    if not os.path.exists(path):
        return STATUS_NULL_POINTER

    os.remove(path)
    return STATUS_SUCCESS