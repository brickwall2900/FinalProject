# Project Goals

- [x] base game
    - [x] typing game
    - [x] tutorial
    - [x] leaderboard
    - [x] save/load
- ~~[ ] profiles~~
- [ ] candy crush
- [ ] wordle
- [x] minesweeper
- [ ] sudoku
- [ ] petdoku
- [?] windows ANSI detection

# Simplification
- [ ] Remove status.py
    - [ ] Rely on if-conditions fo defensive programming
- [ ] Remove terminal.py
- [ ] Remove ansi.py
- [ ] Remove procedures.py
    - [ ] Remove dialog.py
- [ ] Remove common::shuffle
- [ ] Remove common::pick_randomly
- [ ] Inline print() replacing tgfx_...
- [ ] Replace double quote f-strings with single quotes
- [ ] Remove global variables
    - [ ] Everything should be pass by-context or by-parameter
- [ ] Remove inner functions / lambda functions
- [ ] Simplify every fucking function and imports
    - [ ] main.py
    - [ ] parser.py
    - [ ] persistence.py
    - [ ] typing_game.py
    - [ ] minesweeper.py
    - [ ] last_letter.py

By 12 AM, everything should be up and working
- Max number of local imports is 2
- Max number of builtin imports is (os, time, random)
- Max number of branching nests is 3
- Max number of 

i have to rewrite my fucking mental model to simplify code