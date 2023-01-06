"""Tests for pyskvorky.helper module."""
from pyskvorky import helper


def test_player():
    """Test Player class assigns a distinct mutable default value for each instance."""
    # assigning a mutable default value to an instance variable can be tricky; see:
    # https://stackoverflow.com/questions/2681243/how-should-i-declare-default-values-for-instance-variables-in-python
    dummy = "don't care value"
    player1 = helper.Player(dummy, dummy, dummy)
    player2 = helper.Player(dummy, dummy, dummy)
    assert player1.fields == set()
    assert player2.fields == set()

    # at this point both players still may be sharing the same object; let's find out:
    player1.fields.add((0, 0))
    assert player1.fields == {(0, 0)}
    assert player2.fields == set()


def test_envelope():
    """Test envelope() for K=5"""
    # Note: this is not a duplicate test to test_envelope in test_bot:
    # envelope() implementations in both bot.py and helper.py modules are independent

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
    assert helper.envelope((-1, 1), 5) == env5
