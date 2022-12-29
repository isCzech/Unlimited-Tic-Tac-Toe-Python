"""This module implements an Unlimited Tic-Tac-Toe player."""
from collections import Counter
from copy import copy

# Note: it is a part of the API contract that the AI player's main function is called 'play'

# Implementation note: what follows is the simplest implementation of a player I could think of.
# A more interesting approach would implement a player as a class which would allow to create 
# players with strategy modifications by subclassing them from the base player.
# Using modules one has to copy the module in order to create a modified player because,
# unfortunately, a module cannot be imported multiple times with separate namespaces. This:
# import bot as player1
# import bot as player2
# would not work (both would operate over one shared namespace).
# https://stackoverflow.com/questions/37067414/python-import-multiple-times

# constants:
K = 5  # number of consecutive positions marked with the same symbol required to win
R = 3  # neighborhood radius; neighborhood represents all neighbors within R distance

# globals representing the game state:
claimed, lost = set(), set()  # a board consists of two collections representing claimed (owned) and lost positions
next_move_candidates = set()  # all reasonable candidates for the next move
# a move is represented by simply a tuple of coordinates (row, column) with the initial move to (0, 0)
open_lines = set()  # all potentially winning, non-empty lines partially taken exclusively by one player
# next_move_candidates and open_lines are being updated during the game to optimize the computation a bit
# to evaluate the board use a heuristic table of weights to value selected game patterns
# the tables can be generated using the fibonacci sequence for simplicity and easy extendability for K > 5
value_table_opponent = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
value_table_player = [0, 0, 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 144, 233, 377]
# an example of generated evaluation tables for K = 6:
# value_table_opponent = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765]
# value_table_player = [0, 0, 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 2584, 4181, 6765]
# these tables can be used to play the game with K = 6.
pattern_to_index = lambda pattern, count: ((K + 1) * 2 - len(pattern)) * (len(pattern) - 1) // 2 + count
# a heuristic formula converting a (pattern, count) pair to an index into a table of relative weights
# derived manually to provide somewhat satisfactory move evaluation results to beat a mediocre player
# Possible improvement: evaluate recursively for each of opponent's next set of resonable moves


def play(opponents_move):
    # AI player's main function
    # Note: the name 'play' is mandatory as part of the API contract

    if opponents_move is None:  
        # this the first move, place your marker at (0, 0) and update game status accordingly
        update_board((0, 0), claimed, lost)
        return (0, 0)
    else:
        # update board status after opponent's move, select the best countermove and update game status
        # next_move_candidates collect reasonable candidates for the next move evaluation and selection
        update_board(opponents_move, lost, claimed)
        countermove = max(next_move_candidates, key=score)
        update_board(countermove, claimed, lost)
        return countermove


def score(move):
    # copy the board and open_lines collection, evaluate the copies updated with the simalated move
    # and return the score without affecting the previous game state (i.e. the board and open_lines)

    def evaluate_board(fields_collection, value_table):
        # find valuable patterns, evaluate each of them and answer the total value of all patterns
        # valuable patterns are potential winning lines with 2 to 4 player's symbols inside them
        # Note: defining evaluate_board() here allows to use open_lines_ variable set in score()
        c = Counter([line & fields_collection for line in open_lines_])
        e = [value_table[pattern_to_index(pattern, count)] for pattern, count in c.items() if len(pattern) > 1]
        return sum(e)

    claimed_ = copy(claimed)  # no need to copy lost because only claimed_ get updated
    open_lines_ = copy(open_lines)
    # update simulated board state for move
    claimed_.add(move)
    conflicting_lines = [line for line in envelope(move) if not set(line).isdisjoint(lost)]
    open_lines_.update(envelope(move))
    open_lines_.difference_update(conflicting_lines)
    # evaluate the board from both players' point of view
    player_score = evaluate_board(claimed_, value_table_player)
    opponent_score = evaluate_board(lost, value_table_opponent)

    return player_score - opponent_score


def update_board(move, lost, claimed):
    # conflicting_lines is a set of lines that containing a mix of both player's symbols,
    # thus no longer potentially winning lines, thus lines to be removed from open_lines
    # Note: this function is used from both players' perspectives which is a bit confusing
    # TODO: change parameters names to something neutral

    lost.add(move)
    next_move_candidates.update(neighborhood(move))
    next_move_candidates.difference_update(lost | claimed)
    conflicting_lines = {line for line in envelope(move) if not set(line).isdisjoint(claimed)}
    open_lines.update(envelope(move))
    open_lines.difference_update(conflicting_lines)

    
def envelope(position, length=K):
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
    # return all positions within R distance from the given position (row, col)
    # limit radius for the initial few moves to avoid nonsensical choices having identical scores
    radius = max(1, min(R, len(claimed)))
    row, col = position
    neighborhood_ = set()
    for row_ in range(-radius, radius + 1):
        for col_ in range(-radius, radius + 1):
            neighborhood_.add((row + row_, col + col_))
    neighborhood_.remove((row, col))
    return neighborhood_
