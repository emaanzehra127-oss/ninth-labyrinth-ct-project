# ------ GAME SETTINGS AND MAIN STUFF -----------------------
import random #used for randomness (shuffling directions, picking secret words and placing items randomly)
import sys #it is a library imported to check if our code can display symbols - in order to enable it to display symbols - and also for clearing console if we need to
import textwrap #(breaks long sentences into short ones. so they don't look messy on screen)
import subprocess #used to run terminal commands like 'cls' or 'clear' so the screen refreshes cleanly after every move instead of repeating the maze. 
import msvcrt #used to read single key presses (like arrow keys) immediately without needing the Enter key.

#constants for setting up the maze
 
CELLS_WIDE = 9 #measured in cells (width)
CELLS_HIGH = 7 #measured in cells (height)
MAX_HEARTS = 5 #max hearts a player can have
NORMAL_VISION = 2 #how many tiles away the player can see(without a lantern)
LANTERN_VISION = 4 #the number of tiles player can see with a lantern
#removing vision limits would make the maze visible to user from the very first move.
WRAP_WIDTH = 60 #line width used for story-based text(it shows 60 chars on a single line and after that, moves to the other line.)
HINT_MOVES = 4 #no.of hints given to player

#constants to access cheating mode - or whole hints and cheatcode of the game
ADMIN_PASSCODE = 'ct project' #if we type 'admin' then this code unlocks cheatcodes.
ADMIN_COMMANDS = ('answers','reveal','heal') #this is a tuple - and it has words which only admin can use as it contains cheatcodes.

#the constants below(wall,floor,player,exit-tile) are chars
WALL = '#'
FLOOR = '.'
PLAYER = '@'
EXIT_TILE = 'E'

OBJECT_SMYBOLS = {
    'note': 'n',
    'riddle': 'R',
    'potion': '+'
} #its a library used to link tags to their short forms

MOVES = {
    'u': (-1,0), #moves up and is negative since top row is 0 and moving up means going negative that's why we do row-1
    'd': (1,0), #adds 1 to row as it moves down 
    'l': (0,-1), #moves left across cols (left = -ve)
    'r': (0,1), #moves right across cols (right = +ve)
}

MOVE_LETTERS = {
    delta: key for key,
    delta in MOVES.items()
}  #it turns the MOVES dict backward, turning keys into values and values into keys.

SECRET_WORDS = ['NINTH', 'LIGHT', 'ESCAPE', 'SHADOW', 'DAWN', 'FREEDOM']
#this is a list of words among which the system will choose a random word to be the password for the exit

RIDDLES = [ #a list of riddles the system will give out randomly during the exit-finding process.
    {
        'question': 'I speak without a mouth and hear without ears. I come alive when you call out. What am I?',
        'answers': ['echo'],
    },
    {
        'question': 'The more of me you take, the more you leave behind. What am I?',
        'answers': ['footsteps', 'footstep', 'footprints', 'footprint', 'steps'],
    },
    {
        'question': 'I have keys but open no locks. I have space but no room. What am I?',
        'answers': ['keyboard'],
    },
    {
        'question': 'I have hands but cannot clap. What am I?',
        'answers': ['clock', 'watch'],
    },
    {
        'question': 'I resist the flow of current and my unit is the ohm. What am I?',
        'answers': ['resistor', 'resistance'],
    },
    {
        'question': 'I have cities but no houses, mountains but no trees, and water but no fish. What am I?',
        'answers': ['map'],
    },
    {
        'question': 'What number comes next? 2, 4, 8, 16, ...',
        'answers': ['32', 'thirty two', 'thirty-two'],
    }
]

#FUNCTIONS BEGIN HERE

def pick_heart_symbols():
    encoding = sys.stdout.encoding or 'ascii' 
    # it checks whether the terminal is able to render symbols or simply text - no symbols,
    # and if sys.stdout returns NONE, it switches to ascii

    try:
        '\u2665\u2661'.encode(encoding) #tries to translate a filled unicode heart and empty heart into terminal's understandable format.
        return '\u2665', '\u2661' #if the encoding translation passes -  that is, these two symbols translate cleanly, then it returns these two to the program caller.
    except (UnicodeDecodeError, LookupError):
        return '<3', '--' #and in case they don't convert, then symbols get converted to strings of text.

HEART_FULL, HEART_EMPTY = pick_heart_symbols() 
#these are variable names in which the two symbols, full heart and empty heart, are stored


# ---------------- SMALL TEXT HELPERS ---------------------
def say(text):
    print(textwrap.fill(text, WRAP_WIDTH)) #value of wrap_width = 60
    #takes a long string, passes it to textwrap.fill(), whose purpose is to take some text and split it at the 60(WRAP_WIDTH) margin, and prints it.

def ask(prompt):
    return input(prompt).strip()
# it displays a text prompt to player, take whatever they type via input().
# .strip() to delete any accidental leading or trailing spaces before returning it.

#SAY(TEXT) 'PRINTS' BECAUSE IT JUST NEEDS TO DISPLAY DATA ON THE SCREEN.
# ASK(PROMPT) 'RETURNS' BECAUSE IT NEEDS TO PERFORM SOME OPERATION ON IT AND SEND IT BACK TO FUNCTION CALLER.

def get_command():
    """Reads a single keypress: arrow keys move immediately, other keys run commands."""
    key = msvcrt.getch()
    if key in (b'\x00', b'\xe0'): # detects the special prefix sent by arrow keys on Windows
        arrow = msvcrt.getch()
        arrow_map = {
            b'H': 'u', # Up arrow
            b'P': 'd', # Down arrow
            b'K': 'l', # Left arrow
            b'M': 'r', # Right arrow
        }
        return arrow_map.get(arrow, '')
    if key == b'\x03': # allows Ctrl+C to still exit cleanly
        raise KeyboardInterrupt
    try:
        return key.decode('utf-8').lower()
    except UnicodeDecodeError:
        return ''
    
def pause():
    print("\n(Press any key to continue...)")
    msvcrt.getch()

def clean_text(text):
   words = text.lower().strip(".\\!? ").split()
   # whatever words are given, the function first converts it to lowercase
   # then strips away all mentioned punctuation marks from the end of the word.
   # then split the whole word/words on basis of spaces and removes leading or trailing spaces.

   if words and words[0] in ('a', 'an', 'the'):
       words = words[1:]
   # the purpose of checking this condition is to remove any articles from the input (words)
   # because we don't want valid answers from failing simply because a player types a leading article like 'a map' or 'the echo'.
   # instead of just 'map' and 'echo'.

   return ''.join(words) #here, we join all words that we get as inputs into a string NOT HAVING spaces. like a single squashed string w/o any space

def caesar(text, shift): #it encyrpts the secret password using a Caesar Cipher.
    result = ""
    for letter in text.upper(): #forces all letters to be uppercase and then processes them.
        if letter.isalpha(): #checks if letter is an alphabet, and skips punctuation & numbers.
            index = (ord(letter) - ord('A') + shift) % 26
            # the line above turns a capital letter into its normal alphabet number (0 to 25)
            # in computer, A = 65, B = 66, C = 67
            # if letter = C then, math does 67-65 = 2
            # as A=0, B=1, C=2
            # shift moves letter forward (if shift = 3, then 2+3 = 5)
            # %26 is the thing which verifies that if you get 'z' you need to get back to 'A'.
            result += chr(index + ord('A')) # it converts the 0-25 position back into secret code
            # chr converts that code into computer-understandable character.
            #result += keeps on adding this new letter onto your growing encrypted message.

        else:
            result += letter 
    return result

def hearts_text(hearts): # 'hearts' represents the player's current health
    full = [HEART_FULL] * hearts #it creates a list having full-heart symbols, then it multiplies it with remaining health/hearts.
    empty = [HEART_EMPTY] * (MAX_HEARTS - hearts)
    # it creates a list having empty-heart symbols and then multiplies it with hearts/health.
    return ' '.join(full+empty) #it returns a string having both full and empty heart symbols.


# ------------ BUILDING THE LABYRINTH ------------------------

def make_blank_grid(rows, cols): #rows = how tall grid is, cols = how wide grid is
    grid  = [] #we create it cuz in the end, it will hold all of our rows to make the final grid.
    for _ in range(rows): # _ = a throwaway variable 
        #this basically runs a for loop rows times.
        # we use an (_) because we don't really need the number of times the loop is run, we know that it runs a specific number of times, but we don't want to know the exact count.
        # this is because here we're just creating a blank, empty layout.
        row = [] # we create it cuz in the end, all cols are going to be here in this list.
        for _ in range(cols): #now we run for loop 'cols' times
            row.append(WALL) # to list of row, it keeps adding '#' [WALL]
        grid.append(row)
        # and in the end, when row is completely full from lhs to rhs, it appends it our collective grid list.
    return grid

def in_bounds(grid, row, col): #purpose of this func: to make sure row and col and grids are valid, like it's not out of our range!
    #first, check if row = valid
    if 0<=row<len(grid):
        #then check if col = valid
        if 0<=col<len(grid[0]):
            return True
        
    # returns false if both checks fail
    return False

def carve(grid, row, col):
    grid[row][col] = FLOOR # this line makes a current cell by changing position of its rows and cols
                           # with FLOOR as (.), that's the passable path.
    
    directions = list(MOVES.values()) #moves is a dict, so this line gets the values of move(dict)
                                      # and stores them in a list.
    random.shuffle(directions)
    #it randomizes the direction order to ensure the maze generates with an unpredictable
    # and new layout everytime a user plays the game, if we didn't do this - the maze's structure would've been the same everytime.

    for d_row, d_col in directions: # we do this since in directions we have (row,col) as we had moves values.
        next_row = row + 2 * d_row 
        #in line above, we do +2 because we want to ensure that solid walls remain between our corridors.
        #we don't do only 1 because then we would clear all cells in a block, which would create a wide, empty room instead of a wall-based maze.
        next_col = col + 2 * d_col #same logic runs with cols as well over here.
        # We use +2 to intentionally skip over a wall cell and keep it in place, allowing it to serve as a border between pathways.
        if not in_bounds(grid, next_row, next_col): # we check whether the cells fall inside our range, and bounds of the grid.
            continue # we do it to make the loop skip to the next direction's index. so as to prevent index errors.
        if grid[next_row][next_col] == WALL: #it checks if the target cell 2 steps away is still a solid WALL, if it is, it means we can make a floor in it.
            grid[row+d_row][col + d_col] = FLOOR #here, the code just steps one step forward and turns that immediate WALL into a FLOOR.
        # this pattern actually creates a symmetrical grid where every odd-numbered cell = FLOOR, and ever-numbered cell= WALL
            carve(grid, next_row, next_col)
            # this calls carve function recursively.
            # we don't use row and col because we want to move row and col to next_row and next_col so as to advance our maze.


def count_open_neighbors(grid, row, col): #basically, this function checks if the next cell is a floor or not and return it's count.
    count = 0 # count variable to check how many open paths(FLOOR cells) surround the current grid.

    for d_row, d_col in MOVES.values(): #extract values from MOVES dict
        if grid[row + d_row][col + d_col] != WALL: #checks if the next cell is not a WALL.
            count+=1 #if it's not, it's an open floor, so it increments count.

    return count

def find_spots(grid, taken): #this function checks for available spaces in the maze and ignores the taken positions.
    dead_ends = []
    corridors = []

    for row in range(1, len(grid)-1):
        for col in range(1, len(grid[0])-1): 

        # we do len(grid[0]) because grid is a nested list containing many other lists as well. 
        # so the nested list number(height) is the rows of grid, and to access cols, we need to go into each and row and access row[0] means row at index 0.
            if grid[row][col] == WALL or (row, col) in taken: #Checks if the spot is blocked, skipping the cell if it is a WALL or already marked as taken.
                continue #skips to next call since this spot can't be used.
            if count_open_neighbors(grid, row, col) == 1: #checks if we are standing in a position where our next position is a single empty spot.
                dead_ends.append((row, col)) #add rows and cols to dead_ends list.
            else:
                #if cell has more than one empty space next to it
                corridors.append((row, col))
    random.shuffle(dead_ends)
    random.shuffle(corridors)
    return dead_ends + corridors #sends combined list with dead_ends first


def build_objects(spots, secret, shift):
    coded_word = caesar(secret, shift) #builds the coded word by using the caesar function declared in the starting lines.
    riddle_one, riddle_two = random.sample(RIDDLES, 2) #Picks two random riddles out of a list named RIDDLES so that the player gets different puzzles.
    things = [
        {"kind": "note",
            "text": "Scratched into the wall: 'The way out is one "
            "word, but it is written in disguise: "
            + coded_word + "'"}, #this creates a note item that shows the player the scrambled word on the wall.
        {"kind": "note",
            "text": "A torn page reads: 'Every letter of the disguised "
            "word was pushed " + str(shift) + " places forward "
            "in the alphabet. Push each one back to read it.'"}, #this tells the player exactly how many spaces to shift the letters back to decipher a word.
        {"kind": "riddle", "riddle": riddle_one, "reward": "Iron Key"}, #first riddle event, player solves it and gets Iron Key.
        {"kind": "riddle", "riddle": riddle_two, "reward": "Lantern"},  #second riddle event, player solves it and gets Lantern.
        {"kind": "potion"}, #creates a potion that's going to be hidden somewhere in the maze.
        {"kind": "potion"},
        {"kind": "bomb"}, # hides a bomb at a random spot in the maze
        {"kind": "bomb"}, # hides a second bomb at another random spot
        {"kind":"bomb"},
        {"kind":"bomb"},
        {"kind":"bomb"}
    ]  

    placed = {} #an empty list to match specific locations to specific items
    for spot, thing in zip(spots, things): #zip is a built-in function that, in this case, links our list of randomized coordinates
        # with the list of game-items simultaneously.
        # zip() takes the first coordinate and pairs it with the first item, the second coordinate with the second item, and so on. 
        # hence, we can save these pairs in placed{}
        placed[spot] = thing #stores thing as our value in placed dict, and keep spot as the key.

    return placed

def new_game():
    grid = make_blank_grid(2*CELLS_HIGH + 1, 2*CELLS_WIDE + 1)
    # we do cells*2+1 because we need an open path to have a wall beside it, and an extra outer wall to act as a border around entire game.
    start = (1, 1) #defines start row and col for user
    carve(grid, start[0], start[1])
    exit_pos = (len(grid)-2, len(grid[0]) - 2) #it places exit door at bottom-right corner of maze. 
    # we subtract 2 because index -1 is the outer boundary wall, and doing -2 results in the exit being on the very last passable floor inside the maze.
    secret = random.choice(SECRET_WORDS) #picks a random word from list SECRET_WORDS
    shift = random.randint(2, 7) #picks a random number between 2 and 7 to use for scrambling the secret word.
    spots = find_spots(grid, {start, exit_pos})
    # it finds empty places to place items, and makes sure that start and exit positions(i.e. the door) doesn't have one.
    state = {
        'grid': grid, 
        'pos': start, 
        'exit': exit_pos,
        'hearts': MAX_HEARTS, #it saves basic game stats like grid layout, player position, exit spot and starting hearts of player.
        'inventory': [], 
        'notes': [], 
        'objects': build_objects(spots, secret, shift), #it sets up items by an empty inventory list(to track physical tools player picks up, like a Lantern),
        # and notes is an empty list to store text clues found written on the walls.
        # and objects function to map all riddles, notes and potions to their exact location on the maze.
        "secret": secret,
        "shift": shift,
        "admin": False,
        "vision": NORMAL_VISION, #Saves puzzle keys and settings like the secret word, shift code, cheat mode status, and normal view distance
        "seen": set(), # we use a set and not a list because set can't hold duplicate values.
        # and we can instantly look up data in it using hash table lookup, and system just reads that value and not whole number of values.
        "escaped": False,
        "quit": False, #checks game progress by seeing explored areas, and checking if player won or gave up.
        "message": "",
        "moves": 0, # counts total valid steps taken by the player
        "guard": spots[len(spots) // 2], # spawns the guard in an open corridor near the middle of the maze
    } 
    reveal_nearby(state) #it uncovers the map directly around player's starting point so they can see their surroundings clearly.
    return state #it sends back the main game data so main game loop can start running with it.
    #this is because values end when function is stop being called, but to store them permenantly we need to return them to the game/system, so we say return state.

# -------- PATH-FINDING (HINT COMMAND) ----------------

def find_path(grid, current, goal, visited): #a function which searches for a walking path from a current spot to a goal spot, while keeping track of visited places.
    if current == goal:
        return [current] #if current pos = goal pos, simply return current value.
    visited.add(current) #we add the current pos as visited so system doesn't keep moving in circles.
    for d_row, d_col in MOVES.values():
        neighbour = (current[0] + d_row, current[1]+d_col) # we use current[0] as row and current[1] as col since values are stored as (row,col) so 0th index has row and 1st has col.
        if grid[neighbour[0]][neighbour[1]] == WALL: #checks if next neighbor is a wall, hence path = blocked.
            continue #skips this neighbor and onto next direction
        if neighbour in visited: #checks if the neighbor is already visited by user.
            continue #skips this neighbor to avoid making the program run over the same backtrack again and again.
        rest = find_path(grid, neighbour, goal, visited) #recursively calls itself to traverse through every neighbor
        if rest is not None: #it checks if a path to exit was found through recursion.
            return [current] + rest #it adds the current step to the rest of the list, of rest = find_path() and we have to pass it back to function.
    return None #If we check all 4 directions and every single path hits a wall or dead end, we return none so we can turn around and try a different way.

def path_to_moves(path):
    letters = [] #creates an empty list to gather movement letters as user figures them out.
    for index in range(len(path)-1): #loops through whole length of path
        d_row = path[index+1][0] - path[index][0] #finds row change by subtracting the current row from the previous one to see whether user stepped up or down.
        d_col = path[index+1][1] - path[index][1] #finds col change by subtracting the current col from previous one to see whether use moved left or right.
        letters.append(MOVE_LETTERS[(d_row, d_col)]) #it looks up the movement code from MOVE dict and puts that into list of letters.
        
    return letters

# ----------- DRAWING MAP OF MAZE AND ITS STATUS -----------

def reveal_nearby(state): #this function shines a light around player so they can see their surroundings clearly.
    row, col = state['pos'] #it finds where the player is standing right now and saves their row and col number.
    radius = state['vision'] #checks how far the player can see by looking at their current eyesight range(state).
    for check_row in range(row-radius, row+radius+1): # this creates a vision box around the player, to determine how much player can see.
        # row-radius looks for a few steps above the player, and row+radius+1 looks for a few steps below the player.  (+1 for python's range function)
        for check_col in range(col-radius, col+radius+1):
            if in_bounds(state['grid'], check_row, check_col): #checks if the spot is real to prevent system looking outside the edges of game screen.
                state['seen'].add((check_row, check_col)) #remembers this spot by adding it to a secret list of places the player has already seen/visited.

def tile_symbol(state, row, col): #this function decides what symbol to draw on screen for a specific spot.
    pos = (row, col) #puts the spot as (row,col)
    if pos == state['pos']: 
        return PLAYER #it returns the PLAYER(@) if the spot matches where the player is currently standing.
    if pos == state['guard']:
        return 'M' # draws the patrolling guard on the map
    if pos not in state['seen']:
        return ' ' #returns an empty space since player has not seen this spot yet.
    if pos == state['exit']:
        return EXIT_TILE #returns the exit door if spot matches where the maze exit is located.
    thing = state['objects'].get(pos) #it checks for a hidden item by checking if there is a hidden prize or puzzle at that spot.
    if thing is not None: #if an item is found at that spot instead of an empty space.
        if thing['kind'] == 'bomb' and not state['admin']:
            return FLOOR
        return OBJECT_SMYBOLS.get(thing['kind'], '*')

    return state['grid'][row][col] #if no special items, players, or doors are there, it returns normal ground or walls from map grid.

def render(state): #it calls updated maxe grid and converts hidden grid numbers into readable characters line-by-line. 
    print() #to leave a blank clean space at top of screen
    for row in range(len(state['grid'])): #checks all rows of grid
        symbols = []
        for col in range(len(state['grid'][0])): #checks all cols of grid
            symbols.append(tile_symbol(state, row, col)) #it checks what symbol is present in specific spots, and adds them to symbols[].
        print(''.join(symbols)) #joins symbols into single line and prints on screen for player to see

    print(' @ you  E exit  R altar  n note  M guard + potion') #shows player what each symbol means

def show_status(state): #this function prints player's current health status
    items = ', '.join(state['inventory']) or 'nothing' # it lists out your items with commas in b/w, or prints 'nothing' if list is empty.
    tag = ' [ADMIN]' if state['admin'] else '' #it creates a special tag that says [ADMIN] if cheat mode is turned on, otherwise it stays blank.
    print('Hearts:', hearts_text(state['hearts']), '| Moves:', state['moves'], '| Items:', items + tag) #prints health hearts, step count, and items together.

def show_inventory(state): #it lists the items the player carries.
    if not state['inventory']:
        print("Your pockets are empty.") #prints this message if inventory (stock of items) is empty.
        pause()
        return #we use return here because we need to move on since list has no items
    print("You carry:") 
    for item in state['inventory']: #looping through inventory
        print(' -', item) #prints items

def show_journal(state): #it re-reads every note
    if not state['notes']:
        print('You have not found any notes yet.')
        pause()
        return
    print('Your journal:')
    for number, text in enumerate(state['notes'], start=1): #enumerate is used to read out both notes and display their number as well on screen
        say(str(number) + ', ' + text) #prints in this format: (1.Secret note text here.)

def show_help():
    print('Commands (press key directly, no Enter needed):')
    print('  Arrow keys      move up / down / left / right')
    print('  i               inventory')
    print('  j               journal (re-read notes)')
    print('  h               hint: reveals the way out (costs 1 heart)')
    print('  x               admin mode (1: answers, 2: reveal, 3: heal)')
    print('  ?               this help')
    print('  q               quit')
    pause()

# ------- Events: hearts, notes, riddles, potions and the exit door ------
def lose_heart(state, message): #it removes one heart and tells the player why.
    state['hearts'] -= 1
    print()
    say(message + 'You lose a heart!') #gives them warning along with a message that they've lost a heart. 
    print('Hearts:', hearts_text(state['hearts'])) #prints remaining health on screen for player to see.

def read_notes(state, spot, thing): #this function displays the text of the note the player discovered, adds it to notes journal.
    # and removes it from the map dict so it can't be collected again.
    print('\nYou found a note.')
    say(thing['text'])
    state['notes'].append(thing['text'])
    del state['objects'][spot]
    print('(Saved to your journal - press j to read it again.)')
    pause()
    

def give_reward(state, reward): #gives rewards to player
    state['inventory'].append(reward) #adds the reward at end of player's inventory list.
    if reward  == 'Lantern':
        state['vision'] = LANTERN_VISION
        reveal_nearby(state)
        print('The lantern glows. You can see much further now!')
    else: # this runs if player finds another item - like a key or something.
        print('A hidden panel opens. You take the ' + reward + '!') #tells them that they unlocked a door and grabbed their item.

def ask_riddle(state, spot, thing):
    print('You reach a stone altar with words carved on it:')
    say(thing['riddle']['question'])
    print('(Type your answer, or leave to walk away.)')

    while state['hearts'] > 0:
        #it asks a riddle from a player until it is solved, player leaves or hearts get 1.
        answer = clean_text(ask('Answer: '))
        if answer == '':
            print('You must say something.')
        elif answer == "leave":
            print('You step away from the altar.')
            pause()
            return
        elif answer in thing['riddle']['answers']:
            print('Correct! The altar hums.')
            give_reward(state, thing['reward'])
            del state['objects'][spot] #deletes the spot where the riddle was solved, left or hearts ended.
            pause()
            return
        else:
            lose_heart(state, 'Wrong answer!')

def drink_potion(state, spot):
    if state['hearts'] >= MAX_HEARTS:
        print('A healing potion sits here. You feel fine, so you leave it for later.')
        pause()
        return #if health is almost full, no potion allowed.
    state['hearts'] += 1 #here, player drinks potion since hearts number was low, and gains a heart
    del state['objects'][spot] #deletes the potion from map since player drank it.
    print('You drink a healing potion and regain a heart.')
    print(' Hearts:',hearts_text(state['hearts'])) # returns updated health bar.
    pause()

def try_exit_door(state):
    print('A massive iron door blocks the way out.')
    if 'Iron Key' not in state['inventory']: #if iron key is not in inventory items of player.
        state['message'] = 'A massive iron door blocks the way out. It is locked tight and has a keyhole. You need a key from somewhere in the labyrinth.'
        pause()
        return
    say('The Iron Key turns. A cold voice asks for the password.') #if it's there, then run this line.
    print('(Type the password, or leave to step back.)')

    while state['hearts'] > 0:
        answer = ask('Password: ').upper()
        if answer == '':
            print('  You must say something.')
        elif answer == 'LEAVE':
            print('  You step back from the door.')
            pause()
            return
        elif answer == state['secret']: #player answers correctly.
            state['escaped'] = True #that spot is now occupied if answer matches the secret key.
            pause()
            return
        else:
            lose_heart(state, 'The door shudders - wrong word!') #player loses a heart.

def handle_tile(state): #checks what's hiding on the tile(spot) player is standing on right now.
    pos = state['pos'] #saves player's current standing spot
    if pos == state['exit']: #checks if player is standing right at exit.
        try_exit_door(state) #calls escape function
        return
    thing = state['objects'].get(pos) # we see our map dict to see if any hidden item at this spot.
    if thing is None:
        return #it's just an empty tile floor
    if thing['kind'] == 'note': #checks if item is a note
        read_notes(state, pos, thing) 
    elif thing['kind'] == 'riddle':
        ask_riddle(state, pos, thing)
    elif thing['kind'] == 'potion':
        drink_potion(state, pos)
    elif thing['kind'] == 'bomb':
        del state['objects'][pos] # removes the bomb after it explodes so it only triggers once
        state['hearts'] -= 1 # deducts one heart from the player
        state['message'] = 'BOOM! You stepped on a hidden bomb and lost a heart!'

#-------------------COMMANDS------------------------
def bomb_nearby(state):
    """Returns True if a hidden bomb is 1 step away from the player."""
    row, col = state['pos']
    for d_row, d_col in MOVES.values():
        neighbor = (row + d_row, col + d_col)
        thing = state['objects'].get(neighbor)
        if thing is not None and thing['kind'] == 'bomb':
            return True
    return False


def move_guard(state):
    """Moves the patrolling guard 1 random valid step per turn."""
    g_row, g_col = state['guard']
    options = []
    for d_row, d_col in MOVES.values():
        next_tile = (g_row + d_row, g_col + d_col)
        if state['grid'][next_tile[0]][next_tile[1]] != WALL and next_tile != state['exit']:
            options.append(next_tile)
    if options:
        state['guard'] = random.choice(options)
    if state['guard'] == state['pos']:
        state['hearts'] -= 1
        state['message'] = 'A labyrinth guard caught you in the dark! You lose a heart!'


def move_player(state, key): #moving player around a maze when they press a direction key.
    d_row, d_col = MOVES[key]
    new_pos = (state['pos'][0] + d_row, state['pos'][1] + d_col)
    #the above line calculates the new landing position by adding the movt. steps to player's current position.
    if state['grid'][new_pos[0]][new_pos[1]] == WALL: #checks if new landing position blocked by wall.
        state['message'] = 'You bump into a cold stone wall.'
        return
    state['pos'] = new_pos #updates player's position
    state['moves'] += 1 # increments step count on every valid move
    reveal_nearby(state) #shines a light in sourroudings so player can see what's around them.
    handle_tile(state) #checks the new tile to see if there's a note, potion, riddle, or exit door there.
    
    if state['guard'] == state['pos']: # checks if player walked directly into the guard
        state['hearts'] -= 1
        state['message'] = 'You ran straight into a labyrinth guard and lost a heart!'
    else:
        move_guard(state) # moves the guard 1 step after the player moves
     
    if not state['message'] and bomb_nearby(state):
       state['message'] = 'Tick... tick... You hear a faint ticking sound nearby!'

def give_hint(state): #gives hint to user in exchange of health hearts.
    if state['hearts'] <=1 :
        print('You are too weak - a hint would cost your last heart.')
        return
    path = find_path(state['grid'], state['pos'], state['exit'], set()) #finds escape route
    if path is None: #if no exit path exists
        print('The labyrinth stays silent')
        return #Stops the function early and leaves because there are no moves to show you.
    moves = path_to_moves(path) #if path exists, steps are converted into button moves so they're easy to read.
    state['hearts'] -= 1
    print('\nA whisper tells you the way out starts with: ')
    print(' ' + ' -> '.join(moves[:HINT_MOVES])) #Shows the first few moves
    print('(' + str(len(moves)) + 'moves in total.)') #• Tells you the total distance so you know exactly how many steps are left until the exit door.
    print('  You lose a heart! Hearts:', hearts_text(state['hearts']))
    # it reminds you of hea;th cost and shows updated heart health on screen.
    pause()


def describe_object(spot, thing):
    #Admin: print one line (or two) about an unfound object."""
    if thing["kind"] == "riddle": #if it is a riddle, it gives question, and its answer.
        print("Altar at", spot, "-> reward:", thing["reward"])
        print("   Q:", thing["riddle"]["question"])
        print("   Accepted:", ", ".join(thing["riddle"]["answers"]))
    elif thing["kind"] == "note": #if it is a note, it gives the specific spot for obtaining it.
        print("Note at", spot)
    elif thing["kind"] == "bomb":
        print("Hidden bomb at", spot)
    else:
        print("Potion at", spot) #if it is a potion, it gives exact spot to find it.

def show_answers(state):
    #Admin: print the password, the cipher and every puzzle."""
    shift = state["shift"]
    coded = caesar(state["secret"], shift) #the secret text is decoded.
    print("\n--- ADMIN: ANSWERS ---")
    print("Password:", state["secret"]) #since it is admin view, they get the secret password
    print("Disguised as", coded, "(pushed forward by", shift, "places)") #and the name it was disguised in, as well as how many place was it shifted forward.
    print("You are at", state["pos"], " Exit door at", state["exit"]) #tells spot of exit door.
    print("Guard at", state["guard"])
    path = find_path(state["grid"], state["pos"], state["exit"], set()) #helps admin find path.
    if path is not None:
        print("Route to exit:", " ".join(path_to_moves(path))) #tells admin moves to get to the exit.
    for spot, thing in state["objects"].items(): #if no path exists, it tells admin to have hidden powerful objects that will help them land to the exit.
        describe_object(spot, thing)
    print("----------------------")

def reveal_all(state):
    #Admin: mark every tile of the labyrinth as seen, for admin.
    for row in range(len(state["grid"])):
        for col in range(len(state["grid"][0])):
            state["seen"].add((row, col))
    render(state) #this func draw the fully uncovered map, exposing every wall, hidden item, and the exit door to the developer for debugging or testing.

def toggle_admin(state):
    if state["admin"]:
        state["admin"] = False
        print("Admin mode OFF.")
        pause()
        return
    typed = " ".join(ask("Admin passcode: ").lower().split())
    if typed == ADMIN_PASSCODE.lower():
        state["admin"] = True
        print("Admin mode ON. Press 1 (answers), 2 (reveal), or 3 (heal).")
    else:
        print("Wrong passcode.")
    pause()

def handle_command(state, command):
    if command in MOVES:
        move_player(state, command)
    elif command == "x":
        toggle_admin(state)
    elif state["admin"] and command == "1":
        show_answers(state)
        pause()
    elif state["admin"] and command == "2":
        reveal_all(state)
        state["message"] = "Entire labyrinth revealed!"
    elif state["admin"] and command == "3":
        state["hearts"] = MAX_HEARTS
        state["message"] = "Hearts restored: " + hearts_text(state["hearts"])
    elif command == "i":
        show_inventory(state)
        pause()
    elif command == "j":
        show_journal(state)
        pause()
    elif command == "h":
        give_hint(state)
        pause()
    elif command == "?":
        show_help()
        pause()
    elif command == "q":
        state["quit"] = True

#----------------GAME FLOW----------------------

def show_intro():
    #Print the opening story.
    print("\n=== THE NINTH LABYRINTH ===\n")
    say("You wake up on cold stone. The air smells of dust and old "
        "iron. Eight labyrinths have already swallowed their "
        "prisoners. You are in the ninth. Somewhere in the dark "
        "there is a door, a key, and a word that opens it.")
    print()
    say("Solve the riddles, read the clues and decode the password. "
        "Every wrong answer costs a heart. Lose all " + str(MAX_HEARTS)
        + " and you stay here forever.")
    print()
    show_help()

def game_finished(state):
    #True when the player has escaped, died or quit.
    return state["escaped"] or state["quit"] or state["hearts"] <= 0

def show_ending(state):
    #Print the closing message for the finished game.
    print()
    if state["escaped"]:
        #ranks - a tuple 
        #it actually stores number of moves of players wrt the title given to them.
        ranks = ((45, 'S - Master Explorer'), (70, 'A - Escape Artist'), (100, 'B - Survivor'))
        # sets a default fallback rank in case the player took more than 100 moves to escape.
        rank = 'C - Lost Wanderer' #explanation on above line.  #number is the limit. 
        for limit, title in ranks:
            # checks if the player's total moves are less than or equal to the current threshold.
            if state['moves'] <= limit:
                # assigns the matching rank title to the player.
                rank = title
                # stops the loop immediately once the highest earned rank is found so lower ranks don't overwrite it.
                break
        say(f"The door swings open! You escaped in {state['moves']} moves with {state['hearts']} heart(s) left. Rank: {rank}!")
        
    elif state["hearts"] <= 0:
        say("Your last heart fades. The walls close in and the "
            "labyrinth keeps you. The password was "
            + state["secret"] + ".")
    else:
        say("You give up. The labyrinth waits for its next prisoner.")

def play_game():
    """Play one full game from intro to ending."""
    state = new_game()
    show_intro()
    while not game_finished(state):
        subprocess.run('cls' if sys.platform == 'win32' else 'clear', shell=True) #clears the terminal screen before redrawing the updated maze (uses 'cls' on Windows and 'clear' on Mac/Linux) so old copies of the map don't pile up. 
        # sys.platform == 'win32' checks if the user's computer is running Windows.
        
        render(state) #makes a map of maze on screen so player knows where they're standing.
        show_status(state) #prints health hearts and items below the map.
        if state['message']:
            print(state['message'])
            state['message'] = ''
            
        command = get_command() # reads arrow keys or single-letter shortcuts immediately
        handle_command(state, command) #it then executes that command.
    show_ending(state) 

def ask_yes_no(prompt):
    #Keep asking until the player types y or n.
    while True:
        answer = ask(prompt).lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please type y or n.")

def main():
    #Run games until the player decides to stop.
    try:
        while True: 
            play_game()
            if not ask_yes_no("\nPlay again? (y/n): "):
                break
    except (EOFError, KeyboardInterrupt): #it avoids crash error in program.
        #  if a player abruptly cuts off the program by pressing Ctrl+C (a KeyboardInterrupt) or Ctrl+D (an EOFError), this statement catches those events. It gracefully shuts down the game, bypasses the standard error logs, 
        # and prints a polite sign-off message before exiting.
        print()
    print("Thanks for playing The Ninth Labyrinth!")

if __name__ == "__main__":
    main()