"""
Zobrist Hashing for Othello Positions
Provides fast, collision-resistant position identification for caching
"""

import random
from typing import List, Tuple

# Initialize random seed for deterministic hash generation
random.seed(42)

class ZobristHasher:
    """
    Zobrist hashing implementation for Othello positions
    Generates unique 64-bit hashes for board positions
    """
    
    def __init__(self):
        # Generate random 64-bit values for each (square, piece) combination
        # board[r][c] can be: 0 (empty), 1 (black), -1 (white)
        self.piece_hashes = {}
        
        # Hash values for each square and piece combination
        # Use 63 bits to fit in PostgreSQL bigint (signed 64-bit)
        for row in range(8):
            for col in range(8):
                self.piece_hashes[(row, col, 1)] = random.getrandbits(63)   # Black piece
                self.piece_hashes[(row, col, -1)] = random.getrandbits(63)  # White piece
                # Empty squares (0) contribute nothing to hash
        
        # Separate hash for current player to move
        self.player_hash = {
            1: random.getrandbits(63),   # Black to move
            -1: random.getrandbits(63)   # White to move
        }
    
    def compute_hash(self, board: List[List[int]], player: int) -> int:
        """
        Compute Zobrist hash for a board position
        
        Args:
            board: 8x8 board with pieces (0=empty, 1=black, -1=white)
            player: Current player to move (1=black, -1=white)
            
        Returns:
            63-bit hash value uniquely identifying this position (fits in PostgreSQL bigint)
        """
        hash_value = 0
        
        # XOR hash values for all pieces on the board
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece != 0:  # Only non-empty squares contribute
                    hash_value ^= self.piece_hashes[(row, col, piece)]
        
        # XOR with player-to-move hash
        hash_value ^= self.player_hash[player]
        
        return hash_value
    
    def update_hash_after_move(
        self, 
        current_hash: int, 
        board: List[List[int]], 
        old_board: List[List[int]], 
        old_player: int, 
        new_player: int
    ) -> int:
        """
        Incrementally update hash after a move (optimization)
        
        Args:
            current_hash: Hash of the old position
            board: New board state after move
            old_board: Board state before move
            old_player: Player who just moved
            new_player: Player to move next
            
        Returns:
            Updated hash for new position
        """
        hash_value = current_hash
        
        # Remove old player-to-move hash and add new one
        hash_value ^= self.player_hash[old_player]
        hash_value ^= self.player_hash[new_player]
        
        # Update hash for changed squares
        for row in range(8):
            for col in range(8):
                old_piece = old_board[row][col]
                new_piece = board[row][col]
                
                if old_piece != new_piece:
                    # Remove old piece contribution
                    if old_piece != 0:
                        hash_value ^= self.piece_hashes[(row, col, old_piece)]
                    
                    # Add new piece contribution
                    if new_piece != 0:
                        hash_value ^= self.piece_hashes[(row, col, new_piece)]
        
        return hash_value

# Global hasher instance
_hasher = ZobristHasher()

def compute_position_hash(board: List[List[int]], player: int) -> int:
    """
    Convenience function to compute position hash
    
    Args:
        board: 8x8 board state
        player: Current player to move
        
    Returns:
        63-bit Zobrist hash (fits in PostgreSQL bigint)
    """
    return _hasher.compute_hash(board, player)

def update_position_hash(
    current_hash: int, 
    board: List[List[int]], 
    old_board: List[List[int]], 
    old_player: int, 
    new_player: int
) -> int:
    """
    Convenience function to update position hash incrementally
    """
    return _hasher.update_hash_after_move(current_hash, board, old_board, old_player, new_player)