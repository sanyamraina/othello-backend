from typing import List, Optional, Dict
from core.rules import get_valid_moves
from core.board import apply_move


def count_discs(board: List[List[int]]) -> Dict[int, int]:
    counts = {1: 0, -1: 0}
    for row in board:
        for cell in row:
            if cell in counts:
                counts[cell] += 1
    return counts


def make_move(
    board: List[List[int]],
    player: int,
    row: int,
    col: int
):
    new_board = apply_move(board, player, row, col)
    next_player = -player

    next_moves = get_valid_moves(new_board, next_player)

    if not next_moves:
        # Opponent must pass
        next_player = player
        next_moves = get_valid_moves(new_board, player)

    game_over = not next_moves
    winner: Optional[int] = None

    if game_over:
        counts = count_discs(new_board)
        if counts[1] > counts[-1]:
            winner = 1
        elif counts[-1] > counts[1]:
            winner = -1

    return {
    "board": new_board,
    "next_player": next_player,
    "valid_moves": [
        {"row": r, "col": c} for r, c in next_moves
    ],
    "game_over": game_over,
    "winner": winner,
}
