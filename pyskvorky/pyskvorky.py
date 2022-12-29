"""Unlimited Tic-Tac-Toe is a grown-up version of the classic 3x3 game, played by two players on an infinite two-dimensional board. Players try to place 5 consecutive markers in a row (vertical, horizontal or diagonal). The game starts by placing an X marker on any square, usually (0, 0), the 'center' of the infinite board. CONTROLS: arrows move the cursor, return enters player's move, escape quits the game. ALTERNATIVE CONTROLS: WASD as arrows, QEZX move the cursor diagonally, R back to the last move's position, C to the center of the field, space enters a move, shift-Q quits the game.
"""
from argparse import ArgumentParser
from importlib import import_module
import curses
from curses.textpad import rectangle
from time import sleep


## GLOBALS part

# game constants:
K = 5  # number of consecutive positions marked with the same symbol required to win; TODO: make it a parameter

# game control globals:
MAX = 100  # max number of moves; TODO: make it a parameter and introduce a stalemate

# globals for displaying the game state:
yoff, xoff = 5, 5  # offset of the curses screen (playfield) inside the terminal window
buf = 4  # minimum empty space around the outermost marked fields, automatically maintained by `draw_board()`
minsize = 10  # minimum size of the initial playing field (square)


## helper functions and custom exceptions


def winning_set():
    # check whether the board contains a winning line after the last move

    if move is None:  # nothing interesting before the initial move
        return frozenset()
    claimed, _ = board
    winning_lines = {line for line in envelope(move) if move and len(line & claimed) == K}
    return frozenset.union(*winning_lines, frozenset())


def envelope(position, length=K):
    # return all lines containing the position with coordinates given in the position tuple
    # a line represents K consecutive positions (global default K=5) in any direction,
    # i.e. horizontal, vertical or any of the two diagonal
    # e.g. there is 20 lines in an envelope for each position (considering the default K=5)
    # Note: this is a copy of envelope() in bot module; it has to be copied here because the bot module
    # can change it's implementation, name or in general change it's strategy and remove it altogether
    
    row, col = position
    envelope_ = []
    dir_matrix = [(1, 1), (1, 0), (0, 1), (-1, 1)]  # matrix to determine direction
    for dy, dx in dir_matrix:  # each of 4 possible directions has a distinct "signature"
        for i in range(length):  # offset to locate one end of generated lines
            line = []
            for j in range(length):  # length of generated lines
                line.append((row + dy * (i - j), col + dx * (i - j)))
            envelope_.append(frozenset(line))
    return envelope_


class DisplayError(Exception):
    pass


class QuitGame(Exception):
    pass


## PRESENTER part


def draw_board():
    # Note: in Linux the board may contain colored strips depending on the terminal background color
    # I'm not sure how to fix this; in Windows PowerShell the board is drawn flawlessly
    
    ymin, xmin, ymax, xmax = visible_playfield()
    if (yoff + ymax - ymin > curses.LINES - 1) | (xoff + 2*(xmax - xmin) > curses.COLS - 1):
        raise DisplayError  # the size of the requested playfield exceeds the size of the terminal window
        # TODO: instead of raising error the distant part of the playfield could start hiding from view 
    rectangle(screen, yoff, xoff, yoff + ymax - ymin, xoff + 2*(xmax - xmin))  # new frame
    rows = range(ymin + 1, ymax)  # current range of rows
    cols = range(xmin + 1, xmax)  # current range of columns
    field = {(i, j) for i in rows for j in range(1, 2*(xmax - xmin))}  # playing field on the screen
    cross = {(i, j) for i in rows for j in cols if not (i and j)}  # zero axes cross coordinates
    claimed, lost = board
    for i, j in field:
        screen.addstr(yoff + i - ymin, xoff + j, ' ')
    for i, j in cross:
        screen.addstr(yoff + i - ymin, xoff + 2*(j - xmin), '.', curses.A_DIM)
    for i, j in claimed:
        screen.addstr(yoff + i - ymin, xoff + 2*(j - xmin), player_sym, player_style)
    for i, j in lost:
        screen.addstr(yoff + i - ymin, xoff + 2*(j - xmin), opponent_sym, opponent_style)
    i, j = move if move else (0, 0)  # last move's coordinates relative to the board, or (0, 0) before the first move
    y, x = yoff + i - ymin, xoff + 2*(j - xmin)  # last move's position relative to the screen
    if winning_set():  # check for a winning move
        for i, j in winning_set():  # highlight winning lines
            screen.addstr(yoff + i - ymin, xoff + 2*(j - xmin), player_sym, winner_style)
            screen.addstr(y, x, player_sym, winner_style | curses.A_UNDERLINE)
    elif move:  # shortcut for: move is not None, i.e. this is not the initial move
        screen.addstr(y, x, player_sym, player_style | curses.A_UNDERLINE)
    screen.move(y, x)  # place blinking cursor on the last move field
    screen.refresh()


def enter_move(_):
    ymin, xmin, ymax, xmax = visible_playfield()
    while True:
        y, x = screen.getyx()
        row, col = y - yoff + ymin, (x - xoff)//2 + xmin  # current position of the cursor on the playfield (not screen!)
        key = screen.getkey()
        if key in ["c", "KEY_HOME"]:  # move the cursor to (0, 0) field
            screen.move(yoff - ymin, xoff - 2*xmin)
        elif key in ["r", "KEY_END"]:  # move the cursor to last move field
            screen.move(yoff + move[0] - ymin, xoff + 2*(move[1] - xmin))
        elif key in ["a", "KEY_LEFT"]:
            screen.move(y, max(x-2, xoff + 2))
        elif key in ["d", "KEY_RIGHT"]:
            screen.move(y, min(x+2, xoff + 2*(xmax - xmin) - 2))
        elif key in ["w", "KEY_UP"]:
            screen.move(max(y-1, yoff + 1), x)
        elif key in ["s", "KEY_DOWN"]:
            screen.move(min(y+1, yoff + ymax - ymin -1), x)
        elif key in ["q"]:  # move the cursor diagonally up & left
            screen.move(max(y-1, yoff + 1), max(x-2, xoff + 2))
        elif key in ["e"]:  # move the cursor diagonally up & right
            screen.move(max(y-1, yoff + 1), min(x+2, xoff + 2*(xmax - xmin) - 2))
        elif key in ["z"]:  # move the cursor diagonally down & left
            screen.move(min(y+1, yoff + ymax - ymin -1), max(x-2, xoff + 2))
        elif key in ["x"]:  # move the cursor diagonally down & right
            screen.move(min(y+1, yoff + ymax - ymin -1), min(x+2, xoff + 2*(xmax - xmin) - 2))
        elif key in ["Q", chr(27)]:  # chr(27) == "KEY_ESCAPE"; quit the game
            raise QuitGame  # quit the game
            break
        elif key in [" ", chr(10)]:  # chr(10) == "KEY_ENTER"; place your symbol to the field under the cursor
            if (row, col) not in set.union(*board):  # ignore fields already taken, however
                break
    return row, col


def visible_playfield():
    # Return coordinates of the visible part of the board, i.e. upper left and bottom right corners.
    # Note: these are relative to the board, not the curses screen or the rectangle playfield

    if not set.union(*board):  # empty board will be displayed as centered around the (0, 0) position
        return -minsize, -minsize, minsize, minsize
    else:
        ymin, xmin = (min(-minsize, min(i) - buf) for i in zip(*set.union(*board)))  # min coordinates
        ymax, xmax = (max(minsize, max(i) + buf) for i in zip(*set.union(*board)))  # max coordinates
        return ymin, xmin, ymax, xmax


## ARGPARSE part


parser = ArgumentParser(description="Unlimited Tic-Tac-Toe is a grown-up version of the classic 3x3 game, played by two players on an infinite two-dimensional board. Players try to place 5 consecutive markers in a row (vertical, horizontal or diagonal). The game starts by placing an X marker on any square, usually (0, 0), the 'center' of the infinite board. CONTROLS: arrows move the cursor, return enters player's move, escape quits the game. ALTERNATIVE CONTROLS: WASD as arrows, QEZX move the cursor diagonally, R back to the last move's position, C to the center of the field, space enters a move, shift-Q quits the game.", epilog="Enjoy!")

parser.add_argument("-x", "--X_player", default="bot", metavar="<module name> or 'human'",
                    help="assign a player to X marker: default X player is 'bot'")
parser.add_argument("-o", "--O_player", default="human", metavar="<module name> or 'human'",
                    help="assign a player to O marker: default O player is 'human'")
parser.add_argument("-r", "--reverse", action="store_true",
                    help="reverse players; i.e. swap assignments to markers X and O")
parser.add_argument("-d", "--debug", default=False, action="store_true",
                    help="pause bot vs bot game after each move")
parser.add_argument("-s", "--sleep", nargs="?", default=0, const=0.1, type=float, metavar="seconds",
                    help="run sleep timer after each move")
parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.1")

args = parser.parse_args()

X_player = args.X_player
O_player = args.O_player
if args.reverse:
    X_player, O_player = O_player, X_player
sleep_time = args.sleep
step_moves = args.debug and (X_player != 'human') and (O_player != 'human')


## MAIN part


def start_game():
    # Note: this is the most trivial game control mechanism that can be improved in many ways
    # TODO: make MAX a parameter and introduce a stalemate
    # TODO: log the game (moves sequence) into a file
    global move, board, player_sym, opponent_sym, player_play, opponent_play, player_style, opponent_style

    move = None  # last move, represented by a tuple of coordinates (row, column)
    board = (set(), set())  # a board consists of two collections representing claimed (owned) and lost positions
        # relative to a player; player's opponent would see the same board from her point of view, of course

    draw_board()  # draw an empty board for the human player to allow placing the initial move
    for _ in range(MAX):  # TODO: make MAX a parameter and introduce a stalemate
        move = player_play(move)
        sleep(sleep_time)  # insert a delay between displaying each move to simulate thinking :)
        if step_moves:
            screen.getch()  # debug tool: insert a keypress between moves to allow stepping a bot vs bot match
        draw_board()
        claimed, _ = board
        claimed.add(move)
        if winning_set():  # check for a winning move
            draw_board()
            screen.addstr(1, xoff, f"Well done, {player_sym}! Player {opponent_sym} didn't survive {len(claimed)} moves.")
            screen.addstr(2, xoff, f"Press any key to close the curses screen.")
            break
        # swap players before the next move
        player_sym, opponent_sym = opponent_sym, player_sym
        player_play, opponent_play = opponent_play, player_play
        player_style, opponent_style = opponent_style, player_style
        board = board[::-1]  # revert the board before the next move


screen = curses.initscr()  # initialize the curses screen
curses.noecho()  # suppress echoing keypresses
screen.keypad(True)  # enable keypad mode to receive special keys as multibyte escape sequences (e.g. KEY_LEFT)

curses.start_color()  # initalize the default color set
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
winner_style = curses.color_pair(3) | curses.A_BOLD

# a player and an opponent are dynamic entities swapping their contents after each turn
# a much better way to implement them would be a tuple/dictionary or a class
# a player/opponent consist of a function name implementing their strategy, a symbol and a visual style on the screen

# import players dynamically based on the cli parameters --X_player and --O_player; no need to import a human player
# Note: it is a part of the API contract that the AI player's main function is called 'play'
player_play = getattr(import_module(X_player), 'play') if X_player != 'human' else enter_move
opponent_play = getattr(import_module(O_player), 'play') if O_player != 'human' else enter_move

# by default use standard X and O symbols; X usually starts; here player starts, opponent goes next
player_sym = 'X'
opponent_sym = 'O'

player_style = curses.color_pair(1) | curses.A_BOLD
opponent_style = curses.color_pair(2) | curses.A_BOLD

try:
    start_game()
except QuitGame:
    screen.addstr(1, xoff, f"Game interrupted.")
    screen.addstr(2, xoff, f"Press any key to close the curses screen.")
except DisplayError:
    screen.addstr(1, xoff, f"Sorry, can't display.")
    screen.addstr(2, xoff, f"Resize your terminal window and try again.")
    screen.addstr(3, xoff, f"Press any key to close the curses screen.")
    
screen.getch()  # wait for key press before finishing

screen.keypad(False)
curses.echo()
curses.endwin()
