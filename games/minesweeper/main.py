import persistence

import time
import random

from common import safeint, print_error, find, pause
from games.minesweeper.mscommon import to_real_numbers
from games.minesweeper.saveload import __new_game, __save_game, __load_game
from games.minesweeper.ui import __about, __print_congrats, __draw_grid, __user_input, __choose_difficulty
from games.minesweeper.leaderboards import __view_leaderboard

# yay i'm realy proud of this

def call(g_ctx):
    run(g_ctx)

    destroy(g_ctx)

def run(g_ctx):
    game_context = {}
    g_ctx["minesweeper"] = game_context
    
    message = ""
    while True:
        print(" [*] Minesweeper [P]")
        print("Minesweeper is a game where you avoid mines... Don't get blown up!")
        print(" - [1]: Start")
        print(" - [2]: Leaderboards")
        print(" - [3]: About/Information")
        print()
        print(" - [0]: Exit")
        print(message)
        chosen = safeint(input("> "))

        message = ""
        
        if chosen is None:
            message = "Invalid option, try again."
            continue
        
        if chosen == 1:
            game(game_context)
        elif chosen == 2:
            __view_leaderboard(game_context)
        elif chosen == 3:
            __about()
        elif chosen == 0:
            break
        else:
            message = "Invalid option, try again."

def game(game_context):
    saved_game_context = __load_game()
    if not saved_game_context:
        width, height = __choose_difficulty()
        if width is None or height is None:
            return
        __new_game(game_context, width, height)
    else:
        game_context = saved_game_context

    running = True
    while running:
        t = time.time()
        __draw_grid(game_context)
        command = __user_input(game_context)
        dt = time.time() - t
        if len(game_context["mines"]) > 0 and not game_context["dead"]:
            if "tracking_time" in game_context:
                game_context["time"] = game_context["time"] + dt
            else:
                game_context["tracking_time"] = True
                
        running = __process_command(game_context, command)
                
def __process_command(game_context, command):
    TILE_UNKNOWN        = 0
    TILE_MINE           = -1
    TILE_FLAG           = -2
    TILE_CLEAR          = -3
        
    is_game_over = game_context["dead"]

    command = str(command).lower().strip()
    if command == "/exit":
        # ??? profit?
        # wait wtf"?
        if not is_game_over and game_context["dirty"]:
            print("Game board is modified. Save game?")
            print(" - [1]: Yes! <-- default")
            print(" - [2]: No...")
            print(" - [3]: Cancel...")
            
            choice = safeint(input("> "))

            if choice is None and choice == 3:
                return True

            if choice is None or choice != 2:
                success = __save_game(game_context)
                if not success:
                    print_error(f"The game could not be saved...")
                    return True
        return False

    if (command.startswith("x") or command.startswith("f") or command.startswith("s")) and not is_game_over:
        if len(command) < 3:
            print_error("Position x AND y is required.")
            return True
        
        pos_x, pos_y = to_real_numbers(command[2]), to_real_numbers(command[1])

        bad_x, bad_y = pos_x is None, pos_y is None
        if bad_x or bad_y:
            print_error(f"Invalid {'x and y' if bad_x and bad_y else 'x' if bad_x else 'y'} position.")
            return True

        game_width = game_context["width"]
        game_height = game_context["height"]

        assert pos_x is not None and pos_y is not None

        bad_x = pos_x > game_width - 1 or pos_x < 0
        bad_y = pos_y > game_height - 1 or pos_y < 0
        if bad_x or bad_y:
            print_error(f"{'x and y position' if bad_x and bad_y else 'x-position' if bad_x else 'y-position'} is out of bounds")
            return True

        mines = game_context["mines"]
        tiles = game_context["board"]
        first_click = len(mines) == 0
        current_tile_index = pos_y * game_width + pos_x
        current_tile = tiles[current_tile_index]

        def check_tile(x, y):
            tile_index = y * game_width + x
            tile = tiles[tile_index]
            if tile == TILE_FLAG:
                return

            # check if pos is a mine
            if find(mines, (x, y)) is not None:
                # game over lol
                game_context["dead"] = True
                persistence.remove_persistence("minesweeper")
                print("YOU LOST! ;(", "Minesweeper")
                pause()
                for mx, my in mines:
                    tiles[my * game_width + mx] = TILE_MINE
                return

            # okay so if not a mine
            # do shit

            __find_not_mines_algorithm(tiles, mines, x, y, game_width, game_height, tile_index)

        if command.startswith("x"):
            # okay
            # check for first click
            if first_click:
                # if first click, generate mines
                number_of_tiles = game_width * game_height
                number_of_mines = int(number_of_tiles * (random.random() / 20 + .10))
                first_click_safety = []
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        cx, cy = pos_x+i, pos_y+j
                        # ensure in bounds
                        if cx >= 0 and cx < game_width and cy >= 0 and cy < game_height:
                            first_click_safety.append((cx, cy))
                __generate_mines(mines, game_width, game_height, number_of_mines, first_click_safety)
                game_context["flag_count"] = number_of_mines

            check_tile(pos_x, pos_y)
        elif command.startswith("s") and not first_click:
            if current_tile <= 0:
                return True

            flag_count = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    cx, cy = pos_x+i, pos_y+j
                    # ensure in bounds
                    if cx >= 0 and cx < game_width and cy >= 0 and cy < game_height and tiles[cy * game_width + cx] == TILE_FLAG:
                        flag_count += 1

            if flag_count != current_tile:
                return True

            for i in range(-1, 2):
                for j in range(-1, 2):
                    cx, cy = pos_x+i, pos_y+j
                    # ensure in bounds
                    if cx >= 0 and cx < game_width and cy >= 0 and cy < game_height:
                        check_tile(cx, cy)
                        if game_context["dead"]:
                            break
                if game_context["dead"]:
                    break
            
        elif command.startswith("f") and not first_click:
            is_flag = current_tile == TILE_FLAG
            is_unkn = current_tile == TILE_UNKNOWN
            tiles[current_tile_index] = TILE_FLAG if is_unkn else TILE_UNKNOWN if is_flag else current_tile
            flags_taken = -1 if is_unkn else 1 if is_flag else 0
            game_context["flag_count"] = game_context["flag_count"] + flags_taken

        # after it finishes, we need to check for a few things
        all_mines_found = __check_if_mines_are_lonely(tiles, mines, pos_x, pos_y, game_width, game_height, current_tile_index)
        if all_mines_found:
            # the player won
            game_context["dead"] = True
            __print_congrats(game_context)
            return False

        # make game dirty if not won
        game_context["dirty"] = True

    return True

def __check_if_mines_are_lonely(tiles, mines, x, y, w, h, idx):
    TILE_UNKNOWN        = 0
    TILE_MINE           = -1
    TILE_FLAG           = -2
    TILE_CLEAR          = -3

    unrevealed = 0
    for tile_value in tiles:
        if tile_value == TILE_UNKNOWN or tile_value == TILE_FLAG:
            unrevealed += 1
    return unrevealed == len(mines)

def __find_not_mines_algorithm(tiles, mines, x, y, w, h, idx):
    TILE_UNKNOWN        = 0
    TILE_MINE           = -1
    TILE_FLAG           = -2
    TILE_CLEAR          = -3

    # okay we know tiles[idx] is not a mine
    # we then need to find its neighboards and let it think
    checked = [] # add memo to prevent checking already checked
    neighbors = []
    next_neighbors_queue = [(x, y)]
    while True:
        if len(next_neighbors_queue) == 0:
            break

        current_neighbor = next_neighbors_queue.pop(0)
        if find(checked, current_neighbor) is not None:
            continue

        nx, ny = current_neighbor[0], current_neighbor[1]
        if (nx < 0 or nx > w - 1) or (ny < 0 or ny > h - 1): # if neighbor oob then just dont
            continue

        # in order to "queue" that neighbor, it must satisfy some conditions:
        # 1) there must be no mine at that neighbor
        # 2) there must be no adjacnet mine at that neighbor
        if find(mines, (nx, ny)) is not None: # condition 1
            continue

        # ther emust be no adjacent mine at that neighbot
        # but how do we check for adjacemnt mine in the first place?
        adjacent_mine_count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                nax, nay = nx+i, ny+j
                # ensure in bounds
                if nax >= 0 and nax < w and nay >= 0 and nay < h:
                    if find(mines, (nax, nay)) is not None:
                        adjacent_mine_count += 1

        # if we clicked on a tile that has an adjacent mine on it, then skip the algorithm entirely
        if nx == x and ny == y and adjacent_mine_count > 0:
            tiles[idx] = adjacent_mine_count
            break

        # if there are no counted adjacent mines
        # then we can add it to the queued neighbors

        n_idx = ny * w + nx
        if adjacent_mine_count > 0:
            tiles[n_idx] = adjacent_mine_count
            continue
        else:
            tiles[n_idx] = TILE_CLEAR

        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                next_neighbors_queue.append((nx + i, ny + j))
        neighbors.append((nx, ny))
        checked.append((nx, ny))

# i would do the no-guess algorithm if i have time
# but deadline is near so i'd rather do random generation        
def __generate_mines(mines, width, height, number_of_mines, excluded_positions):
    for _ in range(number_of_mines):
        while True:
            mx, my = random.randint(0, width-1), random.randint(0, height-1)
            if find(excluded_positions, (mx, my)) is not None or find(mines, (mx, my)) is not None:
                continue
            mines.append((mx, my))
            break
    
def destroy(g_ctx):
    del g_ctx["minesweeper"]
