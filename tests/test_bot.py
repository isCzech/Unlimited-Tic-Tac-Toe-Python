"""Tests for pyskvorky.bot module."""
from numbers import Number
import pytest
from pyskvorky import bot


def test_globals():
    """Test globals initialization."""
    assert bot.claimed == set()
    assert bot.lost == set()
    assert bot.next_move_candidates == set()
    assert bot.open_lines == set()


@pytest.mark.parametrize('move', [(-1, -2), (1, 1), (0, 0)])
def test_play_subsequent_move(move):
    """Test play() returns a tuple of ints."""
    countermove = bot.play(move)
    assert isinstance(countermove, tuple)
    row, col = countermove
    assert isinstance(row, int)
    assert isinstance(col, int)


@pytest.mark.parametrize('move', [(-1, -2), (1, 1), (0, 0)])
def test_update_board(move):
    """Test update_board() updates the board."""
    assert move in bot.lost


@pytest.fixture
def _init_board():
    """Re-initialize the board"""
    # Note: start the fixture name with '_' to prevent pylint warnings W0621 and W0623
    # this is a pytest/pylint deficiency; recommended fix is the '_' or use 'name' parameter; see:
    # https://stackoverflow.com/questions/46089480/pytest-fixtures-redefining-name-from-outer-scope-pylint
    bot.claimed, bot.lost = set(), set()
    bot.next_move_candidates = set()
    bot.open_lines = set()


def test_initial_move(_init_board):
    """Test bot's initial move."""
    assert bot.play(None) == (0, 0)
    assert bot.claimed == {(0, 0)}
    assert bot.lost == set()


def test_score():
    """Test score() returns a number."""
    assert isinstance(bot.score((0, 0)), Number)


def test_envelope():
    """Test envelope() for K=5"""
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


@pytest.fixture
def _prime_board():
    """Populate the board with 3 moves."""
    bot.claimed, bot.lost = {(0, 0), (0, 1), (0, 2)}, {(-1, 0), (-1, 2)}


@pytest.mark.parametrize('position, radius', [((-1, 1), 1), ((-1, 1), 2), ((-1, 1), 3)])
def test_neighborhood_initial(_init_board, position, radius):
    """Test neighborhood() limits the radius in the first and second move to 1."""
    assert bot.neighborhood(position, radius) == nbr[1]
    bot.claimed = {(0, 0)}  # player's board before the second move (ignore opponent's side)
    assert bot.neighborhood(position, radius) == nbr[1]


@pytest.mark.parametrize('position, radius', [((-1, 1), 1), ((-1, 1), 2), ((-1, 1), 3)])
def test_neighborhood_full(_prime_board, position, radius):
    """Test neighborhood() function after three initial moves without limiting the radius."""
    # Note: use prime_board fixture to populate the board to avoid automatic radius adjustment
    assert bot.neighborhood(position, radius) == nbr[radius]
