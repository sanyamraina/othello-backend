from typing import List, Tuple
from core.rules import get_flips


def apply_move(board: List[List[int]], player: int, row: int, col: int) -> List[List[int]]:
    flips = get_flips(board, player, row, col)
    if not flips:
        raise ValueError("Invalid move")

    new_board = [r[:] for r in board]
    new_board[row][col] = player

    for r, c in flips:
        new_board[r][c] = player

    return new_board
