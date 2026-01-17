from typing import List, Tuple

DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]


def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < 8 and 0 <= c < 8


def get_flips(board: List[List[int]], player: int, row: int, col: int) -> List[Tuple[int, int]]:
    if not in_bounds(row, col):
        return []
    if board[row][col] != 0:
        return []

    opponent = -player
    flips = []

    for dr, dc in DIRECTIONS:
        r, c = row + dr, col + dc
        line = []

        while in_bounds(r, c) and board[r][c] == opponent:
            line.append((r, c))
            r += dr
            c += dc

        if in_bounds(r, c) and board[r][c] == player and line:
            flips.extend(line)

    return flips


def get_valid_moves(board: List[List[int]], player: int) -> List[Tuple[int, int]]:
    moves = []
    for r in range(8):
        for c in range(8):
            if get_flips(board, player, r, c):
                moves.append((r, c))
    return moves
