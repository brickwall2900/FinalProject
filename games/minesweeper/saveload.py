import time
import persistence

from common import safeint, print_error, str_to_bool
from games.minesweeper.mscommon import to_coordinate_numbers, to_real_numbers

# yay i'm realy proud of this

def __new_game(game_context, width, height):
    TILE_UNKNOWN        = 0
    TILE_MINE           = -1
    TILE_FLAG           = -2
    TILE_CLEAR          = -3

    game_context["width"] = width
    game_context["height"] = height

    assert width and height

    game_context["dead"] = False
    game_context["time"] = 0

    # visual boards
    game_context["board"] = [TILE_UNKNOWN] * (width * height)
    game_context["mines"] = [] # tuples of positions
    game_context["flag_count"] = None
    game_context["dirty"] = False # if the board is modified before the game is saved

def __save_game(game_context):
    serialized_game_context = game_context.copy()
    serialized_game_context["time"] = str(int(serialized_game_context["time"] * 100))
    serialized_game_context["board"] = __serialize_board(serialized_game_context["board"])
    serialized_game_context["mines"] = __serialize_mines(serialized_game_context["mines"])
    serialized_game_context["dirty"] = "False"
    success = persistence.save_persistence("minesweeper", serialized_game_context)
    return success

def __load_game():
    ''' returns a game context if to load a saved game, None to start a fresh new game '''

    loaded_game_context = persistence.load_persistence("minesweeper")
    if loaded_game_context is None:
        print("[!] The save file is not found or could not be loaded. Starting a new game instead.")
        return None

    print(f"A save file is found. Last saved: {loaded_game_context['last_saved']}; Want to continue?")
    print(" - [1]: Yes, load it!! <-- default")
    print(" - [2]: No... do NOT load it!! (This will potentially overwrite and delete save data.)")
    
    choice = safeint(input("> "))

    if choice is None or choice != 1:
        return None

    loaded_game_context["width"] = safeint(loaded_game_context["width"])
    loaded_game_context["height"] = safeint(loaded_game_context["height"])

    loaded_game_context["dead"] = str_to_bool(loaded_game_context["dead"])
    loaded_game_context["time"] = safeint(loaded_game_context["time"], 0) / 100

    # visual boards
    loaded_game_context["board"] = __deserialize_board(loaded_game_context["board"])
    if loaded_game_context["board"] is None:
        print_error("Board cannot be read...")
    loaded_game_context["mines"] = __deserialize_mines(loaded_game_context["mines"])
    if loaded_game_context["mines"] is None:
        print_error("Mine data cannot be read...")

    loaded_game_context["flag_count"] = safeint(loaded_game_context["flag_count"])
    loaded_game_context["dirty"] = str_to_bool(loaded_game_context["dirty"])
    loaded_game_context["last_saved"] = time.strftime("%Y-%m-%d %H:%M:%S")

    # as a failsafe
    if loaded_game_context["width"] is None \
        or loaded_game_context["height"] is None \
        or loaded_game_context["dead"] is None \
        or loaded_game_context["time"] is None \
        or loaded_game_context["board"] is None \
        or loaded_game_context["mines"] is None \
        or loaded_game_context["flag_count"] is None \
        or loaded_game_context["dirty"] is None:
        print_error("Save file seems to be corrupt... Starting a new game instead. :\\")
        return None

    return loaded_game_context

def __serialize_board(board):
    TILE_UNKNOWN        = 0
    TILE_MINE           = -1
    TILE_FLAG           = -2
    TILE_CLEAR          = -3
    
    serialized = ""
    for tile in board:
        s = str(tile)

        if tile == TILE_MINE:
            s = "M"
        elif tile == TILE_FLAG:
            s = "F"
        elif tile == TILE_CLEAR:
            s = " "
        elif tile == TILE_UNKNOWN:
            s = "?"

        serialized += s
    return serialized

def __serialize_mines(mines):
    serialized = ""
    for x, y in mines:
        serialized += to_coordinate_numbers(x)
        serialized += to_coordinate_numbers(y)
    return serialized

def __deserialize_mines(serialized):
    mines = []
    xbuf = None
    for ch in serialized:    
        if xbuf is not None:
            ybuf = to_real_numbers(ch)
            if ybuf is None:
                return None
            mines.append((xbuf, ybuf))
            xbuf = None
        else:
            xbuf = to_real_numbers(ch)
            if xbuf is None:
                return None

    return mines

def __deserialize_board(serialized):
    TILE_UNKNOWN        = 0
    TILE_MINE           = -1
    TILE_FLAG           = -2
    TILE_CLEAR          = -3
    
    board = []
    for ch in serialized:    
        tile = safeint(ch)

        if ch == "M":
            tile = TILE_MINE
        elif ch == "F":
            tile = TILE_FLAG
        elif ch == " ":
            tile = TILE_CLEAR
        elif ch == "?":
            tile = TILE_UNKNOWN

        if tile is None:
            return None
        board.append(tile)

    return board
