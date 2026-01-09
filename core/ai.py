from typing import List, Tuple
import random
from core.rules import get_valid_moves


def find_best_move(board: List[List[int]], player: int) -> Tuple[int, int]:
    """
    TEMPORARY AI:
    Picks a random valid move.
    (No heuristics, no evaluation, no minimax)
    """

    moves = get_valid_moves(board, player)

    if not moves:
        raise ValueError("AI called with no valid moves")

    return random.choice(moves)