import pytest


@pytest.fixture
def initial_board():
    board = [[0] * 8 for _ in range(8)]

    # STANDARD OTHELLO START POSITION
    board[3][3] = -1
    board[3][4] = 1
    board[4][3] = 1
    board[4][4] = -1

    return board
