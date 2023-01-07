"""Tests for helper and cli modules."""
from unittest.mock import patch
import pytest
from pyskvorky import helper, cli


argv_list = [  # argv, result
    (['pyskvorky'], ('bot', 'human', 0, False)),
    (['pyskvorky', '-r'], ('human', 'bot', 0, False)),
    (['pyskvorky', '-o', 'rob', '-d'], ('bot', 'rob', 0, True)),
    (['pyskvorky', '-d'], ('bot', 'human', 0, False)),
    (['pyskvorky', '-o', 'rob', '-s', '1'], ('bot', 'rob', 1, False)),
    (['pyskvorky', '-orob', '-s', '1'], ('bot', 'rob', 1, False)),
    (['pyskvorky', '-orob', '-s1'], ('bot', 'rob', 1, False)),
    (['pyskvorky', '-obot'], ('bot', 'bot', 0, False)),
    (['pyskvorky', '-oh'], ('bot', 'h', 0, False)),
]


@pytest.mark.parametrize('argv, result', argv_list, ids=str)
def test_get_cli_args(argv, result):
    """Test parsing correct cli arguments."""
    # Note: let's use mocking instead of setting sys.argv directly
    # https://stackoverflow.com/questions/18668947/how-do-i-set-sys-argv-so-i-can-unit-test-it
    # this is what works too but we're trying to avoid:
    # sys.argv = ['pyskvorky'] + []
    # assert cli.get_cli_args() == ('bot', 'human', 0, False)
    with patch('sys.argv', argv):
        assert cli.get_cli_args() == result


@pytest.mark.parametrize('argv', ['-h', '-v', '-w', '-o', '-x', '-vh', '-ho'], ids=str)
def test_get_cli_args_SystemExit(argv):
    """Test parsing incorrect cli arguments raises SystemExit error."""

    with pytest.raises(SystemExit):
        with patch('sys.argv', ['pyskvorky'] + [argv]):
            cli.get_cli_args()


def test_player():
    """Test Player class assigns a distinct mutable default value for each instance."""
    # assigning a mutable default value to an instance variable can be tricky; see:
    # https://stackoverflow.com/questions/2681243/how-should-i-declare-default-values-for-instance-variables-in-python

    dummy = "don't care value"
    # initialize both player1 and player2 with an empty set of fields
    player1 = helper.Player(dummy, dummy, dummy)
    player2 = helper.Player(dummy, dummy, dummy)
    assert player1.fields == set()
    assert player2.fields == set()

    # at this point both players may still be sharing the same object; let's find out:
    player1.fields.add((0, 0))
    assert player1.fields == {(0, 0)}
    assert player2.fields == set()


def move_player_list():
    """Return a list of arguments and results for test_winning_set"""

    dummy = "don't care value"
    # initialize player1 with a board containg a winning set of fields and player2 with a board without a winning set of fields
    player1 = helper.Player(dummy, dummy, dummy, {(-1, 1), (0, 1), (1, 1), (2, 1), (3, 1), (-3, 3), (-2, 2), (0, 0)})
    player2 = helper.Player(dummy, dummy, dummy, {(-2, 1), (0, 1), (1, 1), (2, 1), (3, 1), (-3, 3), (-2, 2), (0, 0)})
    winning_set = {(-1, 1), (0, 1), (1, 1), (2, 1), (3, 1)}

    return [(None, player1, frozenset()), ((-1, 1), player1, winning_set), ((-1, 1), player2, frozenset())]


@pytest.mark.parametrize('move, player, result', move_player_list())
def test_winning_set(move, player, result):
    """Test winning_set() returns all fields forming a wining line"""

    assert helper.winning_set(move, player) == result



board_contents_list = [
    # board_contents, result
    (None, (-10, -10, 10, 10)),
    ({(-1, 1), (0, 1), (1, 1), (2, 1), (3, 1), (-3, 3)}, (-10, -10, 10, 10)),
    ({(-9, -8), (-4, -2), (-3, -1), (-2, 0), (-1, 7)}, (-13, -12, 10, 11))
]


@pytest.mark.parametrize('board_contents, result', board_contents_list)
def test_visible_playfield(board_contents, result):
    """Test visible_playfield() returns the outer most coordinates of occupied fields plus buffer offset"""

    assert helper.visible_playfield(board_contents) == result


# expected result of envelope((-1, 1))
env = [
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
    """Test envelope() returns all 20 lines"""
    # Note: this is not a duplicate test to test_envelope in test_bot:
    # envelope() implementations in both bot.py and helper.py modules are independent

    assert helper.envelope((-1, 1)) == env
    assert len(helper.envelope((-1, 1))) == 20
