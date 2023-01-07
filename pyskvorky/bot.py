"""This module implements an AI player for the Unlimited Tic-Tac-Toe game."""
from collections import Counter
from copy import copy

# Note: it is a part of the API contract that the AI player's main function is called 'play'

# Implementation note: the following is the simplest implementation of a player I could think of.
# A more robust approach would be to implement a player as a class which would facilitate the
# creation of players with strategy modifications by subclassing them from the base player.
# By using modules one has to copy the module in order to create a modified player because,
# unfortunately, a module cannot be imported multiple times with separate namespaces. This:
# import bot as player1
# import bot as player2
# would not work (both would operate over one shared namespace).
# https://stackoverflow.com/questions/37067414/python-import-multiple-times

# constants:
K = 5  # number of consecutive positions marked with the same symbol required to win
R = 1  # neighborhood radius; neighborhood represents all neighbors within R distance

# globals representing the game state:
claimed, lost = set(), set()  # a board consists of two collections representing claimed (owned) and lost positions
next_move_candidates = set()  # all reasonable candidates for the next move
open_lines = set()  # all potentially winning, non-empty lines partially taken exclusively by one player
# a move is represented by simply a tuple of coordinates (row, column) with the initial move to a position (0, 0)
# next_move_candidates and open_lines are being updated during the game to optimize the computation a bit

# to evaluate the board use a heuristic table of weights to value selected game patterns
# the tables can be generated using the Fibonacci sequence for simplicity and easy extendability for K > 5
# it turns out it's better to use two distinct tables, one for evaluating the board from the player perspective and
# one for evaluating the board from the opponent's perspective; it allows more flexibility to finetune the weights
# Note: consider testing Tribonacci sequence and compare with a player using Fibonacci sequence
value_table_opponent = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
value_table_player = [0, 0, 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 144, 233, 610]
# to better understand the pattern_to_index function here are a few examples:
# a winning pattern containing five symbols in a row maps to index 15 which translates to a value of 610 for the player
# a pattern containing 4 symbols maps to either to index 13 or 14 (depending on how the 4 symbols are spread across the
# winning line) which translates to a value of 144 or 233 for the player or to a value of 233 or 377 for the opponent;
# a pattern containing 3 symbols maps to either of three indexes: 10, 11 or 12 depending on the shape of the pattern

# similarly, evaluation tables for K = 6 can be generated in the same manner using the fibonacci sequence:
# value_table_opponent = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765]
# value_table_player = [0, 0, 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 2584, 4181, 10946]
# replacing the tables and changing the constant K to 6 will allow to play the game.


def play(opponents_move):
    """AI player's main function; receives opponent's move (or None when the game begins) and returns a countermove.
    It uses a heuristics to evaluate each reasonable next move and selects a move with the highest score.
    The function's name 'play' is mandatory as part of the API contract."""

    if opponents_move is None:
        # this the first move, place your marker at (0, 0) and update game status accordingly
        update_board((0, 0), claimed, lost)
        return 0, 0
    # update board status after opponent's move, select the best countermove and update game status
    # next_move_candidates collect reasonable candidates for the next move evaluation and selection
    # IMPROVE: randomize the selection of the countermove from a set of equivalent moves
    # e.g. by adding a random negligible 'noise' to each move's score rather than replacing the max()
    # function below with a random selection from a list of equivalent highest rated moves

    update_board(opponents_move, lost, claimed)
    countermove = max(next_move_candidates, key=score)
    update_board(countermove, claimed, lost)

    return countermove


def update_board(players_move, players_set, opponents_set):
    """Maintains the game status after each move and countermove."""
    # conflicting_lines is a set of lines that containing a mix of both player's symbols,
    # thus no longer potentially winning lines, thus lines that need be removed from open_lines

    players_set.add(players_move)
    next_move_candidates.update(neighborhood(players_move))
    next_move_candidates.difference_update(players_set | opponents_set)
    conflicting_lines = [line for line in envelope(players_move) if not set(line).isdisjoint(opponents_set)]
    open_lines.update(envelope(players_move))
    open_lines.difference_update(conflicting_lines)


def score(move):
    """Evaluates the board from both player's and opponent's perspective and returns the score."""
    # copy the board and open_lines collection, evaluate the copies updated with the simulated move
    # and return the score without affecting the previous game state (i.e. the board and open_lines)
    # IMPROVE: evaluate recursively for each of opponent's next set of reasonable moves

    def evaluate_board(fields_collection, value_table):
        # find valuable patterns, evaluate each of them and answer the total value of all patterns
        # valuable patterns are potential winning lines with 2 to 4 player's symbols inside them
        # Note: defining evaluate_board() here allows to use open_lines_ variable defined in score()
        c = Counter([line & fields_collection for line in open_lines_])
        e = [value_table[pattern_to_index(pattern, count)] for pattern, count in c.items() if len(pattern) > 1]
        return sum(e)

    claimed_ = copy(claimed)  # no need to copy lost because only claimed_ get updated
    open_lines_ = copy(open_lines)
    # update simulated board state for move (same code as in update_board function except next_move_candidates)
    claimed_.add(move)
    conflicting_lines = [line for line in envelope(move) if not set(line).isdisjoint(lost)]
    open_lines_.update(envelope(move))
    open_lines_.difference_update(conflicting_lines)
    # evaluate the board from both players' point of view
    player_score = evaluate_board(claimed_, value_table_player)
    opponent_score = evaluate_board(lost, value_table_opponent)

    return player_score - opponent_score


def pattern_to_index(pattern, count):
    """A heuristic formula converting a (pattern, count) pair to an index into a table of relative weights."""
    # derived manually to provide somewhat satisfactory board evaluation results to beat a mediocre player

    return ((K + 1) * 2 - len(pattern)) * (len(pattern) - 1) // 2 + count


def envelope(position, length=K):
    """A helper function to model all potentially winning scenarios around a given position."""
    # return all lines containing the position with coordinates given in the position tuple
    # a line represents K consecutive positions (global default K=5) in any direction,
    # i.e. horizontal, vertical or any of the two diagonal
    # e.g. there is 20 lines in an envelope for each position (considering the default K=5)
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


def neighborhood(position, radius=R):
    """A helper function to collect all neighboring positions within a given distance from a given position."""

    # limit the radius for the initial few moves to avoid nonsensical choices having equivalent scores
    # Note: is this limiting really necessary? Needs more testing...
    radius = max(1, min(radius, len(claimed)))
    row, col = position
    neighborhood_ = set()
    for row_ in range(-radius, radius + 1):
        for col_ in range(-radius, radius + 1):
            neighborhood_.add((row + row_, col + col_))
    neighborhood_.remove((row, col))
    return neighborhood_
