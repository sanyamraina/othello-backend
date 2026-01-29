from typing import List, Tuple, Optional
import random
from core.rules import get_valid_moves
from core.board import apply_move
from core.evaluation import evaluate_position


def minimax_alpha_beta(
    board: List[List[int]], 
    player: int, 
    depth: int, 
    alpha: float = float('-inf'), 
    beta: float = float('inf'),
    maximizing_player: bool = True
) -> Tuple[float, Optional[Tuple[int, int]]]:
    """
    Minimax algorithm with alpha-beta pruning
    Returns (score, best_move)
    """
    
    # Base case: reached maximum depth or no moves available
    moves = get_valid_moves(board, player)
    if depth == 0 or not moves:
        return evaluate_position(board, player if maximizing_player else -player), None
    
    best_move = None
    
    if maximizing_player:
        max_eval = float('-inf')
        for move in moves:
            r, c = move
            try:
                new_board, _ = apply_move(board, player, r, c)
                
                # Check if opponent has moves, otherwise continue with same player
                opponent = -player
                opp_moves = get_valid_moves(new_board, opponent)
                if opp_moves:
                    eval_score, _ = minimax_alpha_beta(new_board, opponent, depth - 1, alpha, beta, False)
                else:
                    # Opponent has no moves, continue with current player
                    eval_score, _ = minimax_alpha_beta(new_board, player, depth - 1, alpha, beta, True)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning
                    
            except ValueError:
                continue
        
        return max_eval, best_move
    
    else:  # Minimizing player
        min_eval = float('inf')
        for move in moves:
            r, c = move
            try:
                new_board, _ = apply_move(board, player, r, c)
                
                # Check if opponent has moves
                opponent = -player
                opp_moves = get_valid_moves(new_board, opponent)
                if opp_moves:
                    eval_score, _ = minimax_alpha_beta(new_board, opponent, depth - 1, alpha, beta, True)
                else:
                    # Opponent has no moves, continue with current player
                    eval_score, _ = minimax_alpha_beta(new_board, player, depth - 1, alpha, beta, False)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning
                    
            except ValueError:
                continue
        
        return min_eval, best_move


def get_ai_difficulty_depth(difficulty: str = "medium") -> int:
    """Get search depth based on difficulty level"""
    difficulty_map = {
        "easy": 2,
        "medium": 4,
        "hard": 6,
        "expert": 8
    }
    return difficulty_map.get(difficulty.lower(), 4)


def find_best_move(board: List[List[int]], player: int, difficulty: str = "medium") -> Tuple[int, int]:
    """
    Find the best move using minimax with alpha-beta pruning
    """
    moves = get_valid_moves(board, player)
    
    if not moves:
        raise ValueError("AI called with no valid moves")
    
    # For very early game, add some randomness to avoid predictable openings
    filled_squares = sum(1 for row in board for cell in row if cell != 0)
    if filled_squares <= 8 and difficulty != "expert":
        # In opening, sometimes pick a random good move
        if random.random() < 0.3:  # 30% chance of random move in opening
            return random.choice(moves)
    
    depth = get_ai_difficulty_depth(difficulty)
    
    # Use minimax to find best move
    _, best_move = minimax_alpha_beta(board, player, depth, maximizing_player=True)
    
    # Fallback to random if no move found (shouldn't happen)
    if best_move is None:
        return random.choice(moves)
    
    return best_move