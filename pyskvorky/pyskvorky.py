"""Unlimited Tic-Tac-Toe is a grown-up version of the classic 3x3 game, played by two players on an infinite
two-dimensional board. Players try to place 5 consecutive markers in a row (vertical, horizontal or diagonal).
The game starts by placing an X marker on any square, usually (0, 0), the 'center' of the infinite board.
CONTROLS: arrows move the cursor, return enters player's move, escape quits the game. ALTERNATIVE CONTROLS:
WASD as arrows, QEZX move the cursor diagonally, R back to the last move's position, C to the center of the
field, space enters a move, shift-Q quits the game."""

from importlib import import_module
import sys
import curses
from curses.textpad import rectangle
from time import sleep
from cli import get_cli_args
from helper import winning_set, visible_playfield, DisplayError, QuitGame, DuplicatePlayer, Player

# Implementation note: to avoid false pylint E0401 import error, add .pylintrc file to app module as described in:
# https://stackoverflow.com/questions/1899436/pylint-unable-to-import-error-how-to-set-pythonpath
# or another solution (add an example.pth empty file to Python setup folder with the required path to the file):
# https://stackoverflow.com/questions/3402168/permanently-add-a-directory-to-pythonpath


## GLOBAL game parameters


K = 5  # number of consecutive positions marked with the same symbol required to win; IMPROVE: make it a parameter

yoff, xoff = 5, 5  # offset of the curses screen (playfield) inside the terminal window; IMPROVE: make it a parameter


## PRESENTER part


def draw_board():
    """Draw a section of the board containing marked fields; determine the size of the playfield dynamically."""
    # BUG: in Linux the board may contain colored strips depending on the terminal background color
    # Not sure how to fix this; in Windows PowerShell and CMD the board is drawn flawlessly
    # Note: avoid using curses.DIM, it fails to display correctly in Windows CMD

    board_contents = player.fields | opponent.fields  # set of all marked fields
    ymin, xmin, ymax, xmax = visible_playfield(board_contents)
    num_rows, num_cols = screen.getmaxyx()  # get the current size of the physical terminal window
    if (yoff + ymax - ymin > num_rows - 1) | (xoff + 2*(xmax - xmin) > num_cols - 1):
        raise DisplayError  # the size of the requested playfield exceeds the size of the terminal window
        # IMPROVE: instead of raising error, the distant part of the playfield could start sliding away from view
    rectangle(screen, yoff, xoff, yoff + ymax - ymin, xoff + 2*(xmax - xmin))  # new frame
    rows = range(ymin + 1, ymax)  # current range of rows
    cols = range(xmin + 1, xmax)  # current range of columns
    field = {(i, j) for i in rows for j in range(1, 2*(xmax - xmin))}  # playing field on the screen
    cross = {(i, j) for i in rows for j in cols if not (i and j)}  # zero axes cross coordinates
    for i, j in field:
        screen.addstr(yoff + i - ymin, xoff + j, ' ')
    for i, j in cross:
        screen.addstr(yoff + i - ymin, xoff + 2*(j - xmin), '.', cross_style)
    for i, j in player.fields:
        screen.addstr(yoff + i - ymin, xoff + 2*(j - xmin), player.sym, player.style)
    for i, j in opponent.fields:
        screen.addstr(yoff + i - ymin, xoff + 2*(j - xmin), opponent.sym, opponent.style)
    i, j = move if move else (0, 0)  # last move's coordinates relative to the board, or (0, 0) before the first move
    y, x = yoff + i - ymin, xoff + 2*(j - xmin)  # last move's position relative to the screen
    if winning_set(move, player):  # check for a winning move
        for i, j in winning_set(move, player):  # highlight winning lines
            screen.addstr(yoff + i - ymin, xoff + 2*(j - xmin), player.sym, winner_style)
            screen.addstr(y, x, player.sym, winner_style | curses.A_UNDERLINE)
    elif move:  # move is not None, which means this is not the initial move
        screen.addstr(y, x, player.sym, player.style | curses.A_UNDERLINE)
    screen.move(y, x)  # place blinking cursor on the last move field
    screen.refresh()


def enter_move(last_move):
    """Control human player input: allow the player to move cursor inside the playfield to navigate to the desired position;
    return the current cursor position if confirmed as player's intended move; allow the player to quit the game at any time."""

    board_contents = player.fields | opponent.fields  # set of all marked fields
    ymin, xmin, ymax, xmax = visible_playfield(board_contents)
    ylast, xlast = last_move if last_move else (0, 0)
    while True:
        y, x = screen.getyx()  # current cursor position on the physical screen (not the game board)
        row, col = y - yoff + ymin, (x - xoff)//2 + xmin  # current cursor position on the game board
        key = screen.getkey()
        if key in ["c", "KEY_HOME"]:  # move the cursor to the (0, 0) field
            screen.move(yoff - ymin, xoff - 2*xmin)
        elif key in ["r", "KEY_END"]:  # move the cursor to the last move field
            screen.move(yoff + ylast - ymin, xoff + 2*(xlast - xmin))
        elif key in ["a", "KEY_LEFT"]:  # move the cursor one position to the left
            screen.move(y, max(x-2, xoff + 2))
        elif key in ["d", "KEY_RIGHT"]:  # move the cursor one position to the right
            screen.move(y, min(x+2, xoff + 2*(xmax - xmin) - 2))
        elif key in ["w", "KEY_UP"]:  # move the cursor one position up
            screen.move(max(y-1, yoff + 1), x)
        elif key in ["s", "KEY_DOWN"]:  # move the cursor one position down
            screen.move(min(y+1, yoff + ymax - ymin - 1), x)
        elif key in ["q"]:  # move the cursor diagonally up & left
            screen.move(max(y-1, yoff + 1), max(x-2, xoff + 2))
        elif key in ["e"]:  # move the cursor diagonally up & right
            screen.move(max(y-1, yoff + 1), min(x+2, xoff + 2*(xmax - xmin) - 2))
        elif key in ["z"]:  # move the cursor diagonally down & left
            screen.move(min(y+1, yoff + ymax - ymin - 1), max(x-2, xoff + 2))
        elif key in ["x"]:  # move the cursor diagonally down & right
            screen.move(min(y+1, yoff + ymax - ymin - 1), min(x+2, xoff + 2*(xmax - xmin) - 2))
        elif key in ["Q", chr(27)]:  # chr(27) == "KEY_ESCAPE"; quit the game
            raise QuitGame
        elif key in [" ", chr(10)]:  # chr(10) == "KEY_ENTER"; place your symbol to the field under the cursor
            if (row, col) not in board_contents:  # but ignore fields already taken
                break
    return row, col


## GAME CONTROL part


def start_game():
    """A trivial game control mechanism that can be improved in many ways..."""
    # IMPROVE: make MAX a parameter and introduce a stalemate
    # IMPROVE: log the game (moves sequence) into a file
    # IMPROVE: replace global variables
    global move, player, opponent

    max_moves = 100  # max number of moves; IMPROVE: make it a parameter and introduce a stalemate

    draw_board()  # draw an empty board for the human player to allow placing the initial move
    for _ in range(max_moves):  # IMPROVE: make MAX a parameter and introduce a stalemate
        move = player.play(move)
        if player.play != enter_move:  # distinguish between a bot and a human player
            # IMPROVE: this condition deserves refactoring, ideally rename enter_move() and place into a module
            sleep(sleep_time)  # insert a delay between displaying each bot's move to simulate thinking :)
        if step_moves:
            screen.getch()  # debug tool: insert a keypress between moves to allow stepping a bot vs bot match
        player.fields.add(move)
        draw_board()
        if winning_set(move, player):  # check for a winning move
            draw_board()
            screen.addstr(1, xoff, f"Well done, {player.sym}! Player {opponent.sym} lost in {len(player.fields)} moves.")
            screen.addstr(2, xoff, "Press any key to close the curses screen.")
            screen.getch()  # wait for key press to continue
            break
        # swap players before the next move
        player, opponent = opponent, player


## MAIN part


try:
    X_player, O_player, sleep_time, step_moves = get_cli_args()  # get cli arguments

    if X_player == O_player and X_player != 'human':
        # the same AI player module can't be run against itself; maybe in the future...
        raise DuplicatePlayer

    # import players requested via cli arguments --X_player and --O_player; no need to import a human player
    # if the player's module name is not found in the app's directory a ModuleNotFoundError is raised and caught
    # Note: it is a part of the API contract that the AI player's main function is called 'play'
    player1 = getattr(import_module(X_player), "play") if X_player != "human" else enter_move
    player2 = getattr(import_module(O_player), "play") if O_player != "human" else enter_move

except ModuleNotFoundError:
    print("ModuleNotFoundError: Invalid player module name or location.")
    sys.exit()

except DuplicatePlayer:
    print("DuplicatePlayer: You're trying to run the same module twice.")
    sys.exit()

screen = curses.initscr()  # initialize the curses screen
curses.noecho()  # suppress echoing key presses
screen.keypad(True)  # enable keypad mode to receive special keys as multibyte escape sequences (e.g. KEY_LEFT)

curses.start_color()  # initialize the default color set
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)

winner_style = curses.color_pair(3) | curses.A_BOLD
cross_style = curses.color_pair(4)

# a player and an opponent are dynamic entities swapping their contents after each turn
# a board consists of two collections of fields representing player's and opponent's marked positions
# a move represents the last move, i.e. a tuple of coordinates (row, column) representing a position

# by default use standard X and O symbols; X usually starts, hence player starts, opponent goes next
player = Player("X", player1, curses.color_pair(1) | curses.A_BOLD)
opponent = Player("O", player2, curses.color_pair(2) | curses.A_BOLD)

move = None  # initialize to None to indicate the beginning of the game

try:
    start_game()

except QuitGame:
    screen.addstr(1, xoff, "Game interrupted.")
    screen.addstr(2, xoff, "Press any key to close the curses screen.")
    screen.getch()  # wait for key press to continue

except DisplayError:
    screen.addstr(1, xoff, "Can't display your playfield.")
    screen.addstr(2, xoff, "Resize your terminal window and try again.")
    screen.addstr(3, xoff, "Press any key to close the curses screen.")
    screen.getch()  # wait for key press to continue

finally:
    screen.keypad(False)
    curses.echo()
    curses.endwin()  # reset the original terminal window
    # Note: using finally addresses a Linux display issue when terminating the script via CTRL+C interrupt
    # Note: screen.getch() must be outside finally, otherwise the interrupt inside getch() won't be caught
