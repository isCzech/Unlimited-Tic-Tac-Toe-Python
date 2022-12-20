from collections import Counter
from copy import deepcopy, copy
from curses.textpad import rectangle
import curses
import time


# constants:
K = 5  # number of consecutive positions marked with the same symbol required to win
R = 1  # neighborhood radius; neighborhood represents all neighbors within R distance

# globals representing the game state:
move = (0, 0)  # a move is represented by simply a tuple of coordinates (row, column) with the initial move to (0, 0)
board = ({move}, set())  # a board consists of two collections representing claimed (owned) and lost positions
# relative to a player; player's opponent would see the same board from her point of view, of course
next_move_candidates = set()  # all reasonable candidates for the next move
open_lines = set()  # all potentially winning lines (empties don't count, only partially taken ones by either player)
# both next_move_candidates and open_lines are being accumulated during the course of the game to optimize
# the computation a bit; both are associated with a game, not with individual players, i.e. both players share
# the same set of next_move_candidates and open_lines (here's a space for further optimization)

# globals for displaying the game state:
yoff, xoff = 5, 5  # offset of the curses screen (playfield) inside the terminal window
buf = 4  # minimum empty space around the outermost marked fields, automatically maintained by `draw_board()`
minsize = 10  # minimum size of the initial playing field (square)


def start_game():
    global move, board, player_sym, opponent_sym, player_fun, opponent_fun, player_style, opponent_style

    print(f'move {player_sym}: {move}, board: {board}')

    for _ in range(100):
        draw_board()
        player_sym, opponent_sym = opponent_sym, player_sym
        player_fun, opponent_fun = opponent_fun, player_fun
        player_style, opponent_style = opponent_style, player_style
        board = board[::-1]
        move = player_fun(move)
        time.sleep(.1)
        claimed, lost = board
        print(f'move {player_sym}: {move}, score: {score(move)}, '
              f'#candidates: {len(next_move_candidates)}, #openlines: {len(open_lines)}, '
              f'moves played: {player_sym} {len(claimed)}, {opponent_sym} {len(lost)}')
        if winning_lines():  # check for a winning move
            draw_board()
            screen.addstr(1, xoff, f"Game Over, loser! Player {player_sym} won in {len(claimed)} moves.")
            screen.addstr(2, xoff, f"Press any key to close the curses screen.")
            print(f'Game Over, loser!\nPlayer {player_sym} won in {len(claimed)} moves.')
            print_board()
            break


def bot(opponents_move):
    # update board status after opponent's move, select the best countermove and update board status accordingly
    # use next_move_candidates to collect reasonable candidates for the next move to be evaluated
    claimed, lost = board
    update_board(opponents_move, claimed, lost)
    countermove = max(next_move_candidates, key=score)
    update_board(countermove, lost, claimed)

    return countermove


def human(opponents_move):
    # update board status after opponent's move, enter a countermove and update board status accordingly
    claimed, lost = board
    update_board(opponents_move, claimed, lost)
    countermove = enter_move()
    update_board(countermove, lost, claimed)
    
    return countermove


def update_board(move, claimed, lost):
    # use open_lines variable to optimize the computation a bit
    # use conflicting_lines as a set of lines containing a mix of both player's symbols,
    # thus no longer potentially winning lines

    lost.add(move)
    next_move_candidates.update(neighborhood(move))
    next_move_candidates.difference_update(lost | claimed)
    conflicting_lines = {line for line in envelope(move) if not set(line).isdisjoint(claimed)}
    open_lines.update(envelope(move))
    open_lines.difference_update(conflicting_lines)


def score(move):
    # create a copy of the board and open_lines, update the copies to reflect move, evaluate move
    # in the new context and return without affecting the previous game state (i.e. globals)

    def evaluate_board(marked, viewpoint):
        # find valuable patterns, evaluate each of them and answer the total value of all patterns
        # valuable patterns are potential winning lines with 2 to 4 player's symbols inside
        # viewpoint allows to evaluate opponent's situation from the player's perspective
        # use open_lines global to slightly optimize the evaluation

        # to evaluate a board use a heuristic table of weights to value selected game patterns
        # the table uses the fibonacci sequence for simplicity and easier extendability for K > 5
        value_table_opponent = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]  # generated for K=5
        value_table_player = [0, 0, 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 377]  # generated for K=5
        value_table = value_table_opponent if viewpoint=='opponent' else value_table_player

        pattern_to_index = lambda pattern, count: ((K + 1) * 2 - len(pattern)) * (len(pattern) - 1) // 2 + count
        # a heuristic formula converting a (pattern, count) pair to an index into a table of relative weights
        # derived manually to provide somewhat satisfactory move evaluation results to beat a mediocre player

        c = Counter([line & marked for line in open_lines_])
        e = [value_table[pattern_to_index(pattern, count)] for pattern, count in c.items() if len(pattern) > 1]
        return sum(e)

    claimed, lost = deepcopy(board)  # possibly optimize by copy(claimed) only, no deepcopy
    open_lines_ = copy(open_lines)
    # update simulated board state for move
    claimed.add(move)
    conflicting_lines = [line for line in envelope(move) if not set(line).isdisjoint(lost)]
    open_lines_.update(envelope(move))
    open_lines_.difference_update(conflicting_lines)
    # evaluate the board from both players' point of view
    player_score = evaluate_board(claimed, viewpoint='player')
    opponent_score = evaluate_board(lost, viewpoint='opponent')
    return player_score - opponent_score


def envelope(position=(0, 0), length=K):
    # return all k_lines containing the position with coordinates given in the position tuple
    # a k_line represents K consecutive positions (global default K=5) in any direction:
    # horizontal, vertical or any of the two diagonal
    # e.g. there is 20 k_lines in an envelope for each position (considering the default K=5)
    # to-try: lazy-initialize the envelope into a separate dictionary
    # to-try: define position as a class and lazy-initialize the envelope using an instance variable
    row, col = position
    envelope_ = []
    dir_matrix = [(1, 1), (1, 0), (0, 1), (-1, 1)]  # matrix to determine direction
    for dy, dx in dir_matrix:  # each of 4 possible directions has a distinct "signature"
        for i in range(length):  # offset to locate one end of generated lines
            k_line = []
            for j in range(length):  # length of generated lines
                k_line.append((row + dy * (i - j), col + dx * (i - j)))
            envelope_.append(frozenset(k_line))
    return envelope_


def neighborhood(position=(0, 0), radius=R):
    # return all positions within R distance from the given position (row, col)
    row, col = position
    neighborhood_ = set()
    for row_ in range(-radius, radius + 1):
        for col_ in range(-radius, radius + 1):
            neighborhood_.add((row + row_, col + col_))
    neighborhood_.remove((row, col))
    return neighborhood_


def move_gen():
    # move generator for initial debugging in play()
    yield 0, 1
    yield 0, 1
    yield -1, 0
    yield 1, 0
    yield -1, 2


def print_board():
    rows = range(-10, 11)
    cols = range(-10, 11)
    # TODO: adapt ranges to actual board status
    d = {(i, j): ' ' if i and j else '.' for i in rows for j in cols}

    for p in board[0]:  # claimed
        d[p] = player_sym
    for p in board[1]:  # lost
        d[p] = opponent_sym

    for i in rows:
        for j in cols:
            print(d[i, j], end=' ')
        print()


def visible_playfield():
    # Coordinates of the visible part of the board, i.e. upper left and bottom right corners.
    # Note: these are relative to the board, not the curses screen or the rectangle playfield
    ymin, xmin = (min(-minsize, min(i) - buf) for i in zip(*set.union(*board)))  # min coordinates
    ymax, xmax = (max(minsize, max(i) + buf) for i in zip(*set.union(*board)))  # max coordinates
    return ymin, xmin, ymax, xmax


def winning_lines():
    claimed, _ = board
    return {line for line in envelope(move) if len(line & claimed) == K}


def draw_board():
    ymin, xmin, ymax, xmax = visible_playfield()
    if (yoff + ymax - ymin > curses.LINES - 1) | (xoff + 2*(xmax - xmin) > curses.COLS - 1):
        raise ValueError("Can't display exception")
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
    for i, j in frozenset.union(*winning_lines(), frozenset()):  # highlight winning lines
        screen.addstr(yoff + i - ymin, xoff + 2*(j - xmin), player_sym, player_style | curses.A_UNDERLINE)
    i, j = move  # last move's coordinates relative to the board
    y, x = yoff + i - ymin, xoff + 2*(j - xmin)  # last move's position relative to the screen
    screen.addstr(y, x, player_sym, player_style | curses.A_UNDERLINE)
    screen.move(y, x)  # place blinking cursor on the last move field
    screen.refresh()


def enter_move():
    curses.noecho()
    screen.keypad(True)
    while True:
        y, x = screen.getyx()
        ymin, xmin, ymax, xmax = visible_playfield()
        row, col = y - yoff + ymin, (x - xoff)//2 + xmin  # current position of the cursor on the playfield (not screen!)
        key = screen.getkey()
        if key in ["x", "KEY_HOME"]:  # move the cursor to (0, 0) field
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
        elif key in ["c"]:  # move the cursor diagonally down & right
            screen.move(min(y+1, yoff + ymax - ymin -1), min(x+2, xoff + 2*(xmax - xmin) - 2))
        elif key in ["Q", chr(27)]:  # chr(27) == "KEY_ESCAPE"; quit the game
            raise KeyError('Game interrupted exception')
            break
        elif key in [" ", chr(10)]:  # chr(10) == "KEY_ENTER"; place your symbol to the field under the cursor
            if (row, col) not in set.union(*board):  # ignore fields already taken, however
                break
    screen.keypad(False)
        
    return row, col


screen = curses.initscr()  # initialize the curses screen
curses.start_color()  # initalize the default color set
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

player_fun = bot  # first player, symbol 'X'
opponent_fun = human  # second player, symbol 'O'

player_sym = 'X'
opponent_sym = 'O'

player_style = curses.color_pair(1) | curses.A_BOLD
opponent_style = curses.color_pair(2) | curses.A_BOLD

try:
    start_game()
except KeyError:
    screen.addstr(1, xoff, f"Game interrupted; press any key to close the curses screen.")
    print(f"Game interrupted; press any key to close the curses screen.")
    print_board()
except ValueError:
    screen.addstr(1, xoff, f"Sorry, can't display, resize your terminal window and try again.")
    print(f"Sorry, can't display, resize your terminal window and try again.")
    
screen.getch()  # wait for key press and finish
