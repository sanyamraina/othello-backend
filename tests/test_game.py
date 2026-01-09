from core.game import make_move


def test_make_valid_move(initial_board):
    result = make_move(initial_board, 1, 2, 3)

    new_board = result["board"]

    assert new_board[2][3] == 1
    assert new_board[3][3] == 1
    assert result["next_player"] == -1
    assert result["game_over"] is False
