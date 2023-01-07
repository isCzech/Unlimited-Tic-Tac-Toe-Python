"""Helper functions and custom exceptions."""

K = 5  # number of consecutive positions marked with the same symbol required to win; IMPROVE: make it a parameter

buf = 4  # minimum empty space around the outermost marked fields, automatically maintained by draw_board()
minsize = 10  # minimum size of the initial playing field (square)


def winning_set(move, player, length=K):
    """Check whether the board contains a winning line after the last move; return all winning lines."""

    if move is None:  # nothing interesting before the initial move
        return frozenset()
    # collect and return a union of all winning lines in case there are more, not just one
    winning_lines = {line for line in envelope(move) if move and len(line & player.fields) == length}
    return frozenset.union(*winning_lines, frozenset())  # add empty frozenset to prevent .union() error


def envelope(position, length=K):
    """A helper function to model all potentially winning scenarios around a given position."""
    # return all lines containing the position with coordinates given in the position tuple
    # a line represents K consecutive positions (global default K=5) in any direction,
    # i.e. horizontal, vertical or any of the two diagonal
    # e.g. there is 20 lines in an envelope for each position (considering the default K=5)
    # Note: this is a copy of envelope() in bot module; it has to be copied here because the bot module
    # can change its implementation, name or in general change its strategy and remove it altogether

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


def visible_playfield(board_contents):
    """Return coordinates of the upper left and bottom right corners of the part of the board to be displayed;
    it is determined dynamically as the part of the board containing marked fields plus some buffer space around."""
    # Note: the coordinated are relative to the board, not the curses screen or the rectangle playfield

    if not board_contents:  # empty board will be displayed as centered around the (0, 0) position
        return -minsize, -minsize, minsize, minsize  # configurable minimum size to prevent frequent resizing

    ymin, xmin = (min(-minsize, min(i) - buf) for i in zip(*board_contents))  # min coordinates
    ymax, xmax = (max(minsize, max(i) + buf) for i in zip(*board_contents))  # max coordinates

    return ymin, xmin, ymax, xmax


def validate_move(move):
    """Check move is a 2-tuple of ints."""
    # Note: this is just a temporary measure to avoid potential confusing runtime errors
    # start_game() needs refactoring anyway so let's just use asserts for the moment
    # and replace them with proper error handling later; see:
    # https://stackoverflow.com/questions/944592/best-practice-for-using-assert

    assert isinstance(move, tuple)
    assert len(move) == 2

    # now that we know countermove is a 2-tuple, we can safely unpack it
    row, col = move
    assert isinstance(row, int)
    assert isinstance(col, int)

    return move  # returns only when move is validated, otherwise exits via AssertionError


class Player:
    """Simple representation of a player."""
    # a player consists of a symbol, a function name implementing player's strategy, a visual style on the screen
    # and a set of fields marked with the player's symbol during a game
    def __init__(self, sym, play, style, fields=None):
        self.sym = sym
        self.play = play
        self.style = style
        self.fields = fields or set()  # this is a hack to set a distinct mutable default value for each instance
        # https://stackoverflow.com/questions/2681243/how-should-i-declare-default-values-for-instance-variables-in-python
        # setting a mutable default value using dataclasses default_factory is an alternative:
        # fields: set = field(default_factory=set)  # where field is imported from dataclasses


class DisplayError(Exception):
    """A custom exception."""


class QuitGame(Exception):
    """A custom exception."""


class DuplicatePlayer(Exception):
    """A custom exception."""
