"""
Advanced Othello Position Evaluation
Implements sophisticated heuristics for strong AI play
"""

from typing import List, Tuple, Dict
import math
from core.rules import get_valid_moves, DIRECTIONS, in_bounds
from core.board import apply_move


def clamp01(value: float) -> float:
    """Clamp value between 0 and 1"""
    return max(0.0, min(1.0, value))


def game_progress(board: List[List[int]]) -> float:
    """Calculate game progress (0.0 = start, 1.0 = full board)"""
    filled = sum(1 for row in board for cell in row if cell != 0)
    return clamp01(filled / 64.0)


def enhanced_mobility(board: List[List[int]], player: int) -> float:
    """Calculate enhanced mobility (current + potential moves)"""
    opponent = -player
    
    # Current mobility
    my_moves = get_valid_moves(board, player)
    opp_moves = get_valid_moves(board, opponent)
    
    my_current = len(my_moves)
    opp_current = len(opp_moves)
    
    # Potential mobility (empty squares adjacent to opponent pieces)
    my_potential = 0
    opp_potential = 0
    counted = set()
    
    for r in range(8):
        for c in range(8):
            if board[r][c] == 0 and (r, c) not in counted:
                adj_to_my_opp = False
                adj_to_opp_opp = False
                
                for dr, dc in DIRECTIONS:
                    nr, nc = r + dr, c + dc
                    if in_bounds(nr, nc):
                        if board[nr][nc] == opponent:
                            adj_to_my_opp = True
                        if board[nr][nc] == player:
                            adj_to_opp_opp = True
                
                if adj_to_my_opp:
                    my_potential += 1
                if adj_to_opp_opp:
                    opp_potential += 1
                counted.add((r, c))
    
    # Weighted combination: 70% current, 30% potential
    my_total = 0.7 * my_current + 0.3 * my_potential
    opp_total = 0.7 * opp_current + 0.3 * opp_potential
    total = my_total + opp_total
    
    if total == 0:
        return 0.0
    return 100.0 * (my_total - opp_total) / total


def frontier_discs(board: List[List[int]], player: int) -> float:
    """Calculate frontier disc disadvantage (fewer is better)"""
    opponent = -player
    my_frontier = 0
    opp_frontier = 0
    
    for r in range(8):
        for c in range(8):
            if board[r][c] in [player, opponent]:
                is_frontier = False
                
                for dr, dc in DIRECTIONS:
                    nr, nc = r + dr, c + dc
                    if in_bounds(nr, nc) and board[nr][nc] == 0:
                        is_frontier = True
                        break
                
                if is_frontier:
                    if board[r][c] == player:
                        my_frontier += 1
                    else:
                        opp_frontier += 1
    
    total = my_frontier + opp_frontier
    if total == 0:
        return 0.0
    
    # Fewer frontier discs is better (they're vulnerable)
    return 100.0 * (opp_frontier - my_frontier) / total


def enhanced_stability(board: List[List[int]], player: int) -> float:
    """Calculate enhanced stability with multiple stability types"""
    opponent = -player
    stability = [[0 for _ in range(8)] for _ in range(8)]  # 0=unstable, 1=semi, 2=stable
    
    def mark_stable_from_corner(cx: int, cy: int):
        """Mark stable discs from a corner"""
        if board[cx][cy] == 0:
            return
        piece = board[cx][cy]
        
        # Horizontal from corner
        step = 1 if cy == 0 else -1
        for j in range(cy, 8 if cy == 0 else -1, step):
            if not in_bounds(cx, j) or board[cx][j] != piece:
                break
            stability[cx][j] = 2
        
        # Vertical from corner
        step = 1 if cx == 0 else -1
        for i in range(cx, 8 if cx == 0 else -1, step):
            if not in_bounds(i, cy) or board[i][cy] != piece:
                break
            stability[i][cy] = 2
        
        # Diagonal from corner
        di = 1 if cx == 0 else -1
        dj = 1 if cy == 0 else -1
        i, j = cx, cy
        while in_bounds(i, j) and board[i][j] == piece:
            stability[i][j] = 2
            i += di
            j += dj
    
    # Mark stable discs from all corners
    mark_stable_from_corner(0, 0)
    mark_stable_from_corner(0, 7)
    mark_stable_from_corner(7, 0)
    mark_stable_from_corner(7, 7)
    
    # Mark edge-stable discs (full edges)
    for i in range(8):
        # Check if top edge is full of same color
        if board[0][i] != 0 and stability[0][i] == 0:
            edge_piece = board[0][i]
            full_edge = all(board[0][j] == edge_piece for j in range(8))
            if full_edge:
                for j in range(8):
                    stability[0][j] = 2
        
        # Check if bottom edge is full
        if board[7][i] != 0 and stability[7][i] == 0:
            edge_piece = board[7][i]
            full_edge = all(board[7][j] == edge_piece for j in range(8))
            if full_edge:
                for j in range(8):
                    stability[7][j] = 2
        
        # Check if left edge is full
        if board[i][0] != 0 and stability[i][0] == 0:
            edge_piece = board[i][0]
            full_edge = all(board[j][0] == edge_piece for j in range(8))
            if full_edge:
                for j in range(8):
                    stability[j][0] = 2
        
        # Check if right edge is full
        if board[i][7] != 0 and stability[i][7] == 0:
            edge_piece = board[i][7]
            full_edge = all(board[j][7] == edge_piece for j in range(8))
            if full_edge:
                for j in range(8):
                    stability[j][7] = 2
    
    # Count stability scores
    my_stability = 0.0
    opp_stability = 0.0
    
    for r in range(8):
        for c in range(8):
            if board[r][c] == player:
                my_stability += stability[r][c]
            elif board[r][c] == opponent:
                opp_stability += stability[r][c]
    
    total = my_stability + opp_stability
    if total == 0:
        return 0.0
    return 100.0 * (my_stability - opp_stability) / total

def advanced_corner_evaluation(board: List[List[int]], player: int) -> float:
    """Advanced corner evaluation with danger zones"""
    opponent = -player
    my_score = 0.0
    opp_score = 0.0
    
    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    x_squares = [(1, 1), (1, 6), (6, 1), (6, 6)]
    c_squares = [
        [(0, 1), (1, 0), (0, 2), (2, 0), (1, 2), (2, 1)],
        [(0, 6), (1, 7), (0, 5), (2, 7), (1, 5), (2, 6)],
        [(6, 0), (7, 1), (5, 0), (7, 2), (5, 1), (6, 2)],
        [(6, 7), (7, 6), (5, 7), (7, 5), (5, 6), (6, 5)]
    ]
    
    for i, (cx, cy) in enumerate(corners):
        # Corner occupied
        if board[cx][cy] == player:
            my_score += 100  # Huge bonus for corner
        elif board[cx][cy] == opponent:
            opp_score += 100
        else:
            # Corner empty - evaluate access and danger
            xx, xy = x_squares[i]
            
            # X-square penalty (very dangerous)
            if board[xx][xy] == player:
                my_score -= 25
            elif board[xx][xy] == opponent:
                opp_score -= 25
            
            # C-square penalty (moderately dangerous)
            for cx2, cy2 in c_squares[i]:
                if in_bounds(cx2, cy2):
                    if board[cx2][cy2] == player:
                        my_score -= 5
                    elif board[cx2][cy2] == opponent:
                        opp_score -= 5
    
    return my_score - opp_score


def smart_parity(board: List[List[int]], player: int, progress: float) -> float:
    """Parity calculation with endgame bonus"""
    opponent = -player
    my_coins = 0
    opp_coins = 0
    
    for row in board:
        for cell in row:
            if cell == player:
                my_coins += 1
            elif cell == opponent:
                opp_coins += 1
    
    total_coins = my_coins + opp_coins
    if total_coins == 0:
        return 0.0
    
    base_parity = 100.0 * (my_coins - opp_coins) / total_coins
    
    # Endgame bonus: if we're ahead and close to end, huge bonus
    if progress > 0.85 and my_coins > opp_coins:
        base_parity *= (1.0 + 2.0 * (progress - 0.85) / 0.15)
    
    return base_parity

def calculate_tempo(board: List[List[int]], player: int) -> float:
    """Calculate tempo (initiative through forcing moves)"""
    opponent = -player
    
    my_moves = get_valid_moves(board, player)
    opp_moves = get_valid_moves(board, opponent)
    
    # Count "forcing" moves (moves that capture many pieces)
    my_forcing = 0
    opp_forcing = 0
    
    for move in my_moves:
        r, c = move
        try:
            temp_board, flips = apply_move(board, player, r, c)
            if len(flips) >= 3:  # Consider 3+ captures as "forcing"
                my_forcing += 1
        except ValueError:
            continue
    
    for move in opp_moves:
        r, c = move
        try:
            temp_board, flips = apply_move(board, opponent, r, c)
            if len(flips) >= 3:
                opp_forcing += 1
        except ValueError:
            continue
    
    total_forcing = my_forcing + opp_forcing
    if total_forcing == 0:
        return 0.0
    
    return 100.0 * (my_forcing - opp_forcing) / total_forcing


def evaluate_position(board: List[List[int]], player: int) -> float:
    """
    Main evaluation function using advanced heuristics
    Returns a score where positive is good for player, negative is bad
    """
    progress = game_progress(board)
    
    # Adaptive weights based on game phase
    w_corner = 150.0 + 200.0 * progress      # 150→350
    w_mobility = 120.0 - 80.0 * progress     # 120→40
    w_parity = 5.0 + 95.0 * progress         # 5→100
    w_stability = 100.0 + 150.0 * progress   # 100→250
    w_frontier = 60.0 - 30.0 * progress      # 60→30
    w_tempo = 40.0 * (1.0 - progress)        # 40→0
    
    # Calculate all components
    corner_eval = advanced_corner_evaluation(board, player)
    mobility = enhanced_mobility(board, player)
    parity = smart_parity(board, player, progress)
    stability = enhanced_stability(board, player)
    frontier = frontier_discs(board, player)
    tempo = calculate_tempo(board, player)
    
    # Weighted combination
    score = (w_corner * corner_eval / 100.0 +
             w_mobility * mobility / 100.0 +
             w_parity * parity / 100.0 +
             w_stability * stability / 100.0 +
             w_frontier * frontier / 100.0 +
             w_tempo * tempo / 100.0)
    
    return score