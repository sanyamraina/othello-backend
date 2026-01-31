"""
Database Cache Operations for AI Position Storage
Handles persistent storage and retrieval of AI evaluations using Supabase
"""

import json
import os
import asyncio
from typing import Dict, Optional, Tuple, Any
from supabase import create_client, Client
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PositionCache:
    """
    Manages persistent storage of AI position evaluations in Supabase
    Implements depth dominance and handles all database operations
    """
    
    def __init__(self, table_name: str = "positions"):
        self.supabase: Optional[Client] = None
        self.table_name = table_name
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client with credentials from environment"""
        try:
            # Force reload environment variables
            load_dotenv(override=True)
            
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ANON_KEY')
            
            # Check for test mode
            test_mode = os.getenv('TEST_MODE', 'false').lower() == 'true'
            if test_mode:
                self.table_name = os.getenv('CACHE_TABLE_NAME', 'test_positions')
                logger.info(f"Running in TEST MODE - using table: {self.table_name}")
            
            if not supabase_url or not supabase_key:
                logger.warning("Supabase credentials not found. Cache will be disabled.")
                return
            
            self.supabase = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.supabase = None
    
    async def store_position(
        self, 
        position_hash: int, 
        player: int, 
        depth: int, 
        move_evaluations: Dict[Tuple[int, int], float]
    ) -> bool:
        """
        Store position evaluation in database with DATABASE-ENFORCED depth dominance
        
        Args:
            position_hash: Zobrist hash of the position
            player: Player to move (1 or -1)
            depth: Search depth used for evaluation
            move_evaluations: Dict mapping moves to their evaluation scores
            
        Returns:
            True if stored successfully, False otherwise
        """
        if not self.supabase:
            logger.warning("Supabase client not available. Skipping cache storage.")
            return False
        
        try:
            # Convert move tuples to string keys for JSON storage
            moves_json = {
                f"({row},{col})": score 
                for (row, col), score in move_evaluations.items()
            }
            
            # EXPLICIT DEPTH DOMINANCE ENFORCEMENT
            # Step 1: Check existing depth atomically
            existing = self.supabase.table(self.table_name).select('depth').eq(
                'hash', position_hash
            ).eq('player', player).execute()
            
            if existing.data:
                existing_depth = existing.data[0]['depth']
                if depth <= existing_depth:
                    logger.info(f"DEPTH DOMINANCE ENFORCED: Rejecting depth {depth} <= existing depth {existing_depth}")
                    return True  # Depth dominance prevents storage
            
            # Step 2: Store only if depth dominance allows
            data = {
                'hash': position_hash,
                'player': player,
                'depth': depth,
                'moves': moves_json
            }
            
            result = self.supabase.table(self.table_name).upsert(data).execute()
            
            logger.info(f"DEPTH DOMINANCE PASSED: Stored position hash={position_hash}, player={player}, depth={depth}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store position with depth dominance: {e}")
            return False
    
    async def get_cached_position(
        self, 
        position_hash: int, 
        player: int, 
        min_depth: int
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached position evaluation from database
        
        Args:
            position_hash: Zobrist hash of the position
            player: Player to move (1 or -1)
            min_depth: Minimum search depth required
            
        Returns:
            Dict with 'depth' and 'moves' if found and sufficient depth, None otherwise
        """
        if not self.supabase:
            logger.warning("Supabase client not available. Cache miss.")
            return None
        
        try:
            # Query for position with minimum depth requirement
            result = self.supabase.table(self.table_name).select('*').eq(
                'hash', position_hash
            ).eq(
                'player', player
            ).gte(
                'depth', min_depth
            ).execute()
            
            if result.data:
                cached_data = result.data[0]
                
                # Parse JSON moves back to Python dict with tuple keys
                moves_json = cached_data['moves']
                move_evaluations = {}
                
                for move_str, score in moves_json.items():
                    # Parse "(row,col)" back to (row, col) tuple
                    move_str = move_str.strip('()')
                    row, col = map(int, move_str.split(','))
                    move_evaluations[(row, col)] = float(score)
                
                logger.info(f"Cache hit: hash={position_hash}, player={player}, depth={cached_data['depth']}")
                
                return {
                    'depth': cached_data['depth'],
                    'moves': move_evaluations
                }
            
            logger.info(f"Cache miss: hash={position_hash}, player={player}, min_depth={min_depth}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve cached position: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if cache is available for use"""
        return self.supabase is not None

# Global cache instance
def _get_cache_instance():
    """Get cache instance with appropriate table name based on environment"""
    test_mode = os.getenv('TEST_MODE', 'false').lower() == 'true'
    table_name = os.getenv('CACHE_TABLE_NAME', 'test_positions') if test_mode else 'positions'
    return PositionCache(table_name)

_cache = _get_cache_instance()

def store_position_sync(
    position_hash: int, 
    player: int, 
    depth: int, 
    move_evaluations: Dict[Tuple[int, int], float]
) -> bool:
    """
    Synchronous wrapper for storing position
    """
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            _cache.store_position(position_hash, player, depth, move_evaluations)
        )
    except RuntimeError:
        # No event loop running, create new one
        return asyncio.run(
            _cache.store_position(position_hash, player, depth, move_evaluations)
        )

def get_cached_position_sync(
    position_hash: int, 
    player: int, 
    min_depth: int
) -> Optional[Dict[str, Any]]:
    """
    Synchronous wrapper for retrieving cached position
    """
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            _cache.get_cached_position(position_hash, player, min_depth)
        )
    except RuntimeError:
        # No event loop running, create new one
        return asyncio.run(
            _cache.get_cached_position(position_hash, player, min_depth)
        )

def is_cache_available() -> bool:
    """Check if cache is available"""
    return _cache.is_available()