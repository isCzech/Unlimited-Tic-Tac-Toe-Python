"""Tests for pyskvorky.helper module."""
from pyskvorky import helper


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
    assert helper.envelope((-1, 1), 5) == env5


def test_player():
    """Test player class instantiation."""
    player1 = helper.Player('symbol1', 'player1', 'style1')
    assert player1.sym == 'symbol1'
    assert player1.play == 'player1'
    assert player1.style == 'style1'
    assert player1.fields == set()

    player2 = helper.Player('symbol2', 'player2', 'style2')
    assert player2.sym == 'symbol2'
    assert player2.play == 'player2'
    assert player2.style == 'style2'
    assert player2.fields == set()

    # make sure fields attribute is set independently for both players
    player1.fields.add((0, 0))
    assert player1.fields == {(0, 0)}
    assert player2.fields == set()
