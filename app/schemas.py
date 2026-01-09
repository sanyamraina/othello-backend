from pydantic import BaseModel, Field, conint, validator
from typing import List, Optional, Tuple


class Move(BaseModel):
    row: conint(ge=0, le=7)
    col: conint(ge=0, le=7)


class MoveRequest(BaseModel):
    board: List[List[conint(ge=-1, le=1)]] = Field(
        ..., description="8x8 board: 0 empty, 1 black, -1 white"
    )
    player: conint(ge=-1, le=1) = Field(
        ..., description="Current player: 1 (black) or -1 (white)"
    )
    row: Optional[conint(ge=0, le=7)] = Field(
        None, description="Row index (0-7)"
    )
    col: Optional[conint(ge=0, le=7)] = Field(
        None, description="Column index (0-7)"
    )
    use_ai: bool = Field(..., description="Whether to compute AI move")

    @validator("board")
    def validate_board_shape(cls, board):
        if len(board) != 8:
            raise ValueError("Board must have exactly 8 rows")
        for row in board:
            if len(row) != 8:
                raise ValueError("Each board row must have exactly 8 columns")
        return board



class MoveResponse(BaseModel):
    board: List[List[conint(ge=-1, le=1)]]
    next_player: conint(ge=-1, le=1)
    valid_moves: List[Move]
    game_over: bool
    winner: Optional[conint(ge=-1, le=1)] = None

    @validator("board")
    def validate_board_shape(cls, board):
        if len(board) != 8:
            raise ValueError("Board must have exactly 8 rows")
        for row in board:
            if len(row) != 8:
                raise ValueError("Each board row must have exactly 8 columns")
        return board
