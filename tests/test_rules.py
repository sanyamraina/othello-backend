from core.rules import get_valid_moves


def test_initial_valid_moves_black(initial_board):
    moves = get_valid_moves(initial_board, 1)

    expected = {(2, 3), (3, 2), (4, 5), (5, 4)}
    assert set(moves) == expected
