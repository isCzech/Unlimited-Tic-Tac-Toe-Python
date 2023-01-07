"""Tests for pyskvorky.bot module."""
from numbers import Number
from importlib import reload
import pytest
from pyskvorky import bot


@pytest.fixture
def _init_board():
    """Re-initialize the board"""
    # Note: start the fixture name with '_' to prevent pylint warnings W0621 and W0623
    # this is a pytest/pylint deficiency; recommended fix is the '_' prefix or use of 'name' parameter; see:
    # https://stackoverflow.com/questions/46089480/pytest-fixtures-redefining-name-from-outer-scope-pylint

    bot.claimed, bot.lost = set(), set()
    bot.next_move_candidates = set()
    bot.open_lines = set()


@pytest.fixture
def _prime_board():
    """Populate the board with 3 moves."""

    bot.claimed, bot.lost = {(0, 0), (0, 1), (0, 2)}, {(-1, 0), (-1, 2)}


def test_globals():
    """Test globals are initialized to empty sets after import."""
    # Note: we must reload the module to test the initialization status because if some other tests
    # are run prior this one the status of the globals may chenge and the test would fail

    reload(bot)
    assert bot.claimed == set()
    assert bot.lost == set()
    assert bot.next_move_candidates == set()
    assert bot.open_lines == set()


@pytest.mark.parametrize('move', [None, (-1, -2), (0, 0)], ids=str)
def test_play(move):
    """Test play() returns a 2-tuple of ints."""

    countermove = bot.play(move)
    assert isinstance(countermove, tuple)
    assert len(countermove) == 2

    # now that we know countermove is a 2-tuple, we can safely unpack it
    row, col = countermove
    assert isinstance(row, int)
    assert isinstance(col, int)


@pytest.mark.parametrize('move', [(-1, -2), (0, 0)], ids=str)
def test_update_board(_init_board, move):
    """Test update_board() updates the board with move and countermove."""
    # Note: ignore open_lines and next_move_candidates for the moment

    countermove = bot.play(move)
    assert move in bot.lost
    assert countermove in bot.claimed


def test_initial_move(_init_board):
    """Test bot's initial move and the board after the move."""

    assert bot.play(None) == (0, 0)
    assert bot.claimed == {(0, 0)}
    assert bot.lost == set()


# patterns, counts and expected results of pattern_to_index(pattern, count)
# count indicates the number of occurences of the pattern in a potentially winning line;
# note that the more occurences the less blocked and more valuable the pattern is
# e.g. four positions pattern can occur either once in a line or twice depending on whether
# both ends of the pattern on the board are free or just one end is free or whether there's
# a free position inside the pattern, i.e. the pattern is not contiguous (see second item).
# Note: the list doesn't exhaust all possible situations for single position patterns
pattern_count_list = [  # pattern, count, expected result
    [{(-5, -3), (-4, -2), (-3, -1), (-2, 0), (-1, 1)}, 1, 15],
    [{(-5, -3), (-4, -2), (-3, -1), (-2, 0)},          2, 14],
    [{(-5, -3), (-4, -2),           (-2, 0), (-1, 1)}, 1, 13],
    [{(-5, -3), (-4, -2), (-3, -1)},                   3, 12],
    [{(-5, -3), (-4, -2),           (-2, 0)},          2, 11],
    [{(-5, -3),           (-3, -1),          (-1, 1)}, 1, 10],
    [{(-5, -3), (-4, -2)},                             4, 9],
    [{(-5, -3),           (-3, -1)},                   3, 8],
    [{(-5, -3),                     (-2, 0)},          2, 7],
    [{(-5, -3),                              (-1, 1)}, 1, 6],
    [{(-5, -3)},                                       5, 5],
    [{(-5, -3)},                                       1, 1],
]


@pytest.mark.parametrize('pattern, count, result', pattern_count_list, ids=str)
def test_pattern_to_index(pattern, count, result):
    """Test score() returns a number."""

    assert bot.pattern_to_index(pattern, count) == result


def test_score():
    """Test score() returns a number."""

    assert isinstance(bot.score((0, 0)), Number)


# expected result of envelope((-1, 1), 5)
env5 = [
    frozenset({(-5, -3), (-4, -2), (-3, -1), (-2, 0), (-1, 1)}),
    frozenset({(-4, -2), (-3, -1), (-2, 0), (-1, 1), (0, 2)}),
    frozenset({(-3, -1), (-2, 0), (-1, 1), (0, 2), (1, 3)}),
    frozenset({(-2, 0), (-1, 1), (0, 2), (1, 3), (2, 4)}),
    frozenset({(-1, 1), (0, 2), (1, 3), (2, 4), (3, 5)}),
    frozenset({(-5, 1), (-4, 1), (-3, 1), (-2, 1), (-1, 1)}),
    frozenset({(-4, 1), (-3, 1), (-2, 1), (-1, 1), (0, 1)}),
    frozenset({(-3, 1), (-2, 1), (-1, 1), (0, 1), (1, 1)}),
    frozenset({(-2, 1), (-1, 1), (0, 1), (1, 1), (2, 1)}),
    frozenset({(-1, 1), (0, 1), (1, 1), (2, 1), (3, 1)}),
    frozenset({(-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1)}),
    frozenset({(-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2)}),
    frozenset({(-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3)}),
    frozenset({(-1, 0), (-1, 1), (-1, 2), (-1, 3), (-1, 4)}),
    frozenset({(-1, 1), (-1, 2), (-1, 3), (-1, 4), (-1, 5)}),
    frozenset({(-1, 1), (0, 0), (1, -1), (2, -2), (3, -3)}),
    frozenset({(-2, 2), (-1, 1), (0, 0), (1, -1), (2, -2)}),
    frozenset({(-3, 3), (-2, 2), (-1, 1), (0, 0), (1, -1)}),
    frozenset({(-4, 4), (-3, 3), (-2, 2), (-1, 1), (0, 0)}),
    frozenset({(-5, 5), (-4, 4), (-3, 3), (-2, 2), (-1, 1)})
]


def test_envelope():
    """Test envelope() for K=5"""

    assert bot.envelope((-1, 1), 5) == env5


# expected results of neighborhood((-1, 1), radius) for radius = 1, 2 and 3
nbr = {
    1: {(-2, 0), (-2, 1), (-2, 2), (-1, 0), (-1, 2), (0, 0), (0, 1), (0, 2)},
    2: {(-3, 0), (-3, 3), (0, 2), (1, 0), (1, 3), (-2, -1), (-1, -1), (-2, 1),
        (-3, 2), (0, -1), (0, 1), (1, 2), (-2, 0), (-1, 0), (-2, 3), (-1, 3),
        (-2, 2), (-3, -1), (-3, 1), (0, 0), (1, 1), (0, 3), (1, -1), (-1, 2)},
    3: {(-3, 0), (-3, 3), (0, 2), (2, 2), (1, 0), (1, 3), (-4, -2), (-4, -1),
        (-4, 4), (-4, 1), (-2, -2), (-2, -1), (-2, 4), (-1, -2), (-2, 1), (-1, -1),
        (-1, 4), (-3, 2), (0, -2), (0, -1), (0, 1), (2, -2), (2, -1), (1, 2),
        (0, 4), (2, 1), (2, 4), (-4, 0), (-4, 3), (-2, 0), (-1, 0), (-2, 3),
        (-1, 3), (-1, 2), (-3, -2), (-3, -1), (-3, 4), (-3, 1), (0, 0), (1, 1),
        (0, 3), (2, 0), (1, -2), (1, -1), (1, 4), (2, 3), (-4, 2), (-2, 2)}
    }


@pytest.mark.parametrize('position, radius', [((-1, 1), 1), ((-1, 1), 2), ((-1, 1), 3)], ids=str)
def test_neighborhood_initial(_init_board, position, radius):
    """Test neighborhood() function limits the radius in the first move to 1."""

    assert bot.neighborhood(position, radius) == nbr[1]


@pytest.mark.parametrize('position, radius', [((-1, 1), 1), ((-1, 1), 2), ((-1, 1), 3)], ids=str)
def test_neighborhood_full(_prime_board, position, radius):
    """Test neighborhood() function won't limit the radius after the initial few (three) moves."""
    # Note: use prime_board fixture to populate the board to avoid automatic radius adjustment

    assert bot.neighborhood(position, radius) == nbr[radius]
