from pydantic import BaseModel, Field
from typing import List, Optional


class MoveRequest(BaseModel):
    board: List[List[int]] = Field(..., description="Current board state")
    player: int = Field(..., description="Current player: 1 (black) or -1 (white)")
    row: Optional[int] = Field(None, description="Row index for human move")
    col: Optional[int] = Field(None, description="Column index for human move")
    use_ai: bool = Field(..., description="Whether backend should compute AI move")


class MoveResponse(BaseModel):
    board: List[List[int]] = Field(..., description="Updated board state")
    next_player: int = Field(..., description="Next player: 1 or -1")
    valid_moves: List[List[int]] = Field(..., description="List of valid moves for next player")
    game_over: bool = Field(..., description="Whether the game has ended")
    winner: Optional[int] = Field(None, description="Winner: 1, -1, or None")
