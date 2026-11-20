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
- [x] word bomb
- [x] math murder
- [ ] word search?
- [ ] sudoku
- [ ] petdoku
- [ ] documentation
    - [ ] main.py
    - [ ] parser.py
    - [ ] persistence.py
    - [ ] common.py
    - [x] comparators.py ? (remove this file)
    - [ ] word_bank.py
    - [ ] motd.py
    - [ ] typing_game/*
    - [ ] minesweper/*
    - [ ] last_letter/*
- [?] windows ANSI detection

# Simplification
- [x] Remove status.py
    - [ ] Rely on if-conditions fo defensive programming
- [x] Remove terminal.py
- [x] Remove ansi.py
- [x] Remove procedures.py
    - [x] Remove dialog.py
- [x] Remove common::shuffle
- [x] Remove common::pick_randomly
- [x] Inline print() replacing tgfx_...
- [x] Replace double quote f-strings with single quotes
- [x] Remove global variables
    - [x] Everything should be pass by-context or by-parameter
- [ ] Remove inner functions / lambda functions
- [ ] No usage of functions as a variable (functions first-class)
- [x] Simplify every fucking function and imports
    - [x] main.py
    - [x] parser.py
    - [x] persistence.py
    - [x] typing_game.py
    - [x] minesweeper.py
    - [x] last_letter.py

By 12 AM, everything should be up and working
- 3:38 AM; It is past 12 and everything is still not fucking working.

# Arbitrary Rules That I Hopefully Won't Fucking Break
- Max number of local imports is 2
- Max number of builtin imports is (os, time, random)
- Max number of branching nests is 3
- Max number of functions in one file is 10
- Functions exceeding 50 lines are not allowed

i have to rewrite my fucking mental model to simplify code