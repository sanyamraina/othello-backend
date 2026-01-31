"""
Difficulty Selection Policies for Othello AI
Implements authentic difficulty levels through move selection strategies
"""

import random
from typing import Dict, Tuple, List
import logging

logger = logging.getLogger(__name__)

class DifficultySelector:
    """
    Implements different selection policies for AI difficulty levels
    All policies use the same cached evaluation data but select moves differently
    """
    
    @staticmethod
    def select_hard_move(move_evaluations: Dict[Tuple[int, int], float]) -> Tuple[int, int]:
        """
        Hard difficulty: Select move with highest evaluation score
        
        Args:
            move_evaluations: Dict mapping moves to evaluation scores
            
        Returns:
            Best move (row, col)
        """
        if not move_evaluations:
            raise ValueError("No moves available for selection")
        
        # Select move with maximum evaluation
        best_move = max(move_evaluations.items(), key=lambda x: x[1])
        
        logger.debug(f"Hard difficulty selected: {best_move[0]} with score {best_move[1]:.3f}")
        return best_move[0]
    
    @staticmethod
    def select_medium_move(
        move_evaluations: Dict[Tuple[int, int], float], 
        k: int = 3
    ) -> Tuple[int, int]:
        """
        Medium difficulty: Randomly select from top-K highest scoring moves
        
        Args:
            move_evaluations: Dict mapping moves to evaluation scores
            k: Number of top moves to consider (default: 3)
            
        Returns:
            Selected move (row, col)
        """
        if not move_evaluations:
            raise ValueError("No moves available for selection")
        
        # Sort moves by evaluation score (highest first)
        sorted_moves = sorted(move_evaluations.items(), key=lambda x: x[1], reverse=True)
        
        # Take top-K moves (or all if fewer than K available)
        top_moves = sorted_moves[:min(k, len(sorted_moves))]
        
        # Randomly select from top moves
        selected_move = random.choice(top_moves)
        
        logger.debug(f"Medium difficulty selected: {selected_move[0]} with score {selected_move[1]:.3f} from top {len(top_moves)}")
        return selected_move[0]
    
    @staticmethod
    def select_easy_move(
        move_evaluations: Dict[Tuple[int, int], float],
        noise_factor: float = 0.3,
        center_bias: float = 0.1
    ) -> Tuple[int, int]:
        """
        Easy difficulty: Add noise and heuristic bias to move selection
        
        Args:
            move_evaluations: Dict mapping moves to evaluation scores
            noise_factor: Amount of random noise to add (default: 0.3)
            center_bias: Bonus for center moves (default: 0.1)
            
        Returns:
            Selected move (row, col)
        """
        if not move_evaluations:
            raise ValueError("No moves available for selection")
        
        # Create noisy evaluations
        noisy_evaluations = {}
        
        for move, score in move_evaluations.items():
            row, col = move
            
            # Add random noise
            noise = random.uniform(-noise_factor, noise_factor)
            noisy_score = score + noise
            
            # Add center bias (prefer moves closer to center)
            center_distance = abs(row - 3.5) + abs(col - 3.5)
            center_bonus = center_bias * (7 - center_distance) / 7
            noisy_score += center_bonus
            
            noisy_evaluations[move] = noisy_score
        
        # Select move with highest noisy evaluation
        selected_move = max(noisy_evaluations.items(), key=lambda x: x[1])
        
        original_score = move_evaluations[selected_move[0]]
        logger.debug(f"Easy difficulty selected: {selected_move[0]} with original score {original_score:.3f}, noisy score {selected_move[1]:.3f}")
        
        return selected_move[0]
    
    @staticmethod
    def select_expert_move(move_evaluations: Dict[Tuple[int, int], float]) -> Tuple[int, int]:
        """
        Expert difficulty: Same as hard but with potential for deeper analysis
        Currently identical to hard difficulty
        
        Args:
            move_evaluations: Dict mapping moves to evaluation scores
            
        Returns:
            Best move (row, col)
        """
        return DifficultySelector.select_hard_move(move_evaluations)

def select_move_by_difficulty(
    move_evaluations: Dict[Tuple[int, int], float], 
    difficulty: str
) -> Tuple[int, int]:
    """
    Select move based on difficulty level
    
    Args:
        move_evaluations: Dict mapping moves to evaluation scores
        difficulty: Difficulty level ("easy", "medium", "hard", "expert")
        
    Returns:
        Selected move (row, col)
        
    Raises:
        ValueError: If difficulty is invalid or no moves available
    """
    if not move_evaluations:
        raise ValueError("No moves available for selection")
    
    difficulty = difficulty.lower()
    selector = DifficultySelector()
    
    if difficulty == "easy":
        return selector.select_easy_move(move_evaluations)
    elif difficulty == "medium":
        return selector.select_medium_move(move_evaluations)
    elif difficulty == "hard":
        return selector.select_hard_move(move_evaluations)
    elif difficulty == "expert":
        return selector.select_expert_move(move_evaluations)
    else:
        raise ValueError(f"Invalid difficulty level: {difficulty}. Must be one of: easy, medium, hard, expert")

def get_search_depth_for_difficulty(difficulty: str) -> int:
    """
    Get consistent search depth regardless of difficulty
    In the new system, difficulty affects selection, not search depth
    
    Args:
        difficulty: Difficulty level
        
    Returns:
        Search depth to use (currently fixed at 6 for all difficulties)
    """
    # For now, use consistent depth across all difficulties
    # This can be made configurable later
    return 6