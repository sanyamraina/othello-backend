"""
Advanced Othello AI with Persistent Caching
Implements Negamax search with transposition table and difficulty selection policies
"""

from typing import List, Tuple, Dict, Optional
import random
import logging
from core.rules import get_valid_moves
from core.board import apply_move
from core.evaluation import evaluate_position
from core.zobrist import compute_position_hash
from core.cache import store_position_sync, get_cached_position_sync, is_cache_available
from core.difficulty import select_move_by_difficulty, get_search_depth_for_difficulty

logger = logging.getLogger(__name__)

def negamax_search(
    board: List[List[int]], 
    player: int, 
    depth: int, 
    alpha: float = float('-inf'), 
    beta: float = float('inf'),
    collect_root_evaluations: bool = False
) -> Tuple[float, Optional[Tuple[int, int]], Optional[Dict[Tuple[int, int], float]]]:
    """
    Negamax algorithm with alpha-beta pruning
    All scores are from current player's perspective
    
    Args:
        board: Current board state
        player: Current player (1 or -1)
        depth: Remaining search depth
        alpha: Alpha value for pruning
        beta: Beta value for pruning
        collect_root_evaluations: If True, collect all move evaluations at root
        
    Returns:
        Tuple of (score, best_move, move_evaluations)
        move_evaluations is only populated at root level when collect_root_evaluations=True
    """
    
    # Base case: reached maximum depth or no moves available
    moves = get_valid_moves(board, player)
    if depth == 0 or not moves:
        score = evaluate_position(board, player)
        return score, None, None
    
    best_move = None
    best_score = float('-inf')
    move_evaluations = {} if collect_root_evaluations else None
    
    for move in moves:
        row, col = move
        try:
            new_board, _ = apply_move(board, player, row, col)
            
            # Check if opponent has moves
            opponent = -player
            opp_moves = get_valid_moves(new_board, opponent)
            
            if opp_moves:
                # Opponent can move - recurse with opponent
                score, _, _ = negamax_search(new_board, opponent, depth - 1, -beta, -alpha, False)
                score = -score  # Negate for current player's perspective
            else:
                # Opponent has no moves - continue with current player
                score, _, _ = negamax_search(new_board, player, depth - 1, alpha, beta, False)
            
            # Collect evaluations at root level
            if collect_root_evaluations:
                move_evaluations[move] = score
            
            # Update best move and score
            if score > best_score:
                best_score = score
                best_move = move
            
            # Alpha-beta pruning
            alpha = max(alpha, score)
            if alpha >= beta:
                break  # Beta cutoff
                
        except ValueError:
            # Invalid move, skip
            continue
    
    return best_score, best_move, move_evaluations

def find_best_move_with_cache(
    board: List[List[int]], 
    player: int, 
    difficulty: str = "medium"
) -> Tuple[Tuple[int, int], bool, int]:
    """
    Find the best move using cached evaluations or fresh search
    
    Args:
        board: Current board state
        player: Current player (1 or -1)
        difficulty: Difficulty level for move selection
        
    Returns:
        Tuple of (selected_move, cache_hit, search_depth)
    """
    moves = get_valid_moves(board, player)
    
    if not moves:
        raise ValueError("AI called with no valid moves")
    
    # Single move - no need for search
    if len(moves) == 1:
        logger.info("Only one legal move available")
        return moves[0], False, 0
    
    # Get search depth (consistent across difficulties)
    search_depth = get_search_depth_for_difficulty(difficulty)
    
    # Compute position hash for cache lookup
    position_hash = compute_position_hash(board, player)
    
    # Try to get cached evaluations
    move_evaluations = None
    cache_hit = False
    cached_depth = 0
    
    if is_cache_available():
        cached_result = get_cached_position_sync(position_hash, player, search_depth)
        if cached_result:
            move_evaluations = cached_result['moves']
            cache_hit = True
            cached_depth = cached_result['depth']
            logger.info(f"Cache hit: Using cached evaluations from depth {cached_depth}")
    
    # If no cache hit, run fresh search
    if not cache_hit:
        logger.info(f"Cache miss: Running fresh search at depth {search_depth}")
        
        # Run negamax search and collect all move evaluations
        _, _, move_evaluations = negamax_search(
            board, player, search_depth, collect_root_evaluations=True
        )
        
        if not move_evaluations:
            logger.warning("Search failed to produce evaluations, falling back to random")
            return random.choice(moves), False, search_depth
        
        # Store evaluations in cache
        if is_cache_available():
            success = store_position_sync(position_hash, player, search_depth, move_evaluations)
            if success:
                logger.info("Stored position evaluations in cache")
            else:
                logger.warning("Failed to store position in cache")
    
    # Apply difficulty-based selection policy
    try:
        selected_move = select_move_by_difficulty(move_evaluations, difficulty)
        actual_depth = cached_depth if cache_hit else search_depth
        logger.info(f"Selected move {selected_move} using {difficulty} difficulty")
        return selected_move, cache_hit, actual_depth
        
    except Exception as e:
        logger.error(f"Error in move selection: {e}")
        return random.choice(moves), False, search_depth

def find_best_move(board: List[List[int]], player: int, difficulty: str = "medium") -> Tuple[int, int]:
    """
    Main entry point for AI move selection
    Maintains compatibility with existing API
    
    Args:
        board: Current board state
        player: Current player (1 or -1)
        difficulty: Difficulty level
        
    Returns:
        Selected move (row, col)
    """
    try:
        move, _, _ = find_best_move_with_cache(board, player, difficulty)
        return move
    except Exception as e:
        logger.error(f"AI move selection failed: {e}")
        # Fallback to random move
        moves = get_valid_moves(board, player)
        if moves:
            return random.choice(moves)
        else:
            raise ValueError("No valid moves available")

# Legacy function for backward compatibility
def get_ai_difficulty_depth(difficulty: str = "medium") -> int:
    """
    Legacy function - now returns consistent depth
    Kept for backward compatibility
    """
    return get_search_depth_for_difficulty(difficulty)