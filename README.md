# The Ninth Labyrinth

The Ninth Labyrinth is a terminal-based maze and puzzle game written in Python. You wake up inside a dark, randomly generated labyrinth with 5 hearts and limited visibility, and your goal is to find the exit door before your health runs out. To unlock the exit, you have to explore the map, solve two stone altars (`R`) to get the Iron Key and a Lantern, and collect two hidden wall notes (`n`) that give you an encrypted password and the Caesar-cipher shift needed to decode it.

To make the gameplay challenging and smooth in the terminal, the screen refreshes in place after every move using `subprocess`, and arrow keys move your character (`@`) immediately via `msvcrt` without needing to press Enter. Five invisible bombs are hidden across the maze—walking next to one triggers a faint ticking warning so you can avoid stepping on it, while a patrolling guard (`M`) roams the corridors every turn. When you finally escape, the game counts your total steps and assigns a final rank (`S`, `A`, `B`, or `C`).

We built the whole game using standard Python concepts instead of external game engines—dictionaries keep track of player stats and hidden objects, tuples store grid coordinates and rank limits, sets remember which tiles you have already seen, and recursion generates a new maze layout every run while also powering the hint command (`h`). To play, run `python final_code.py` in a Windows terminal (or press `x` and type `ct project` during the game to open Admin Mode for testing).

