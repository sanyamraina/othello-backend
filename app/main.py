from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, conint, validator
from typing import List
import os
from dotenv import load_dotenv

from core.game import make_move, count_discs
from core.ai import find_best_move, find_best_move_with_cache
from core.rules import get_valid_moves
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Schemas ----------

class MoveRequest(BaseModel):
    board: List[List[conint(ge=-1, le=1)]]
    player: conint(ge=-1, le=1)
    row: conint(ge=0, le=7)
    col: conint(ge=0, le=7)

    @validator("player")
    def validate_player(cls, player):
        if player == 0:
            raise ValueError("Player must be 1 or -1")
        return player

    @validator("board")
    def validate_board_shape(cls, board):
        if len(board) != 8:
            raise ValueError("Board must have exactly 8 rows")
        for row in board:
            if len(row) != 8:
                raise ValueError("Each board row must have exactly 8 columns")
        return board

class AIMoveRequest(BaseModel):
    board: List[List[conint(ge=-1, le=1)]]
    player: conint(ge=-1, le=1)
    difficulty: str = "medium"  # easy, medium, hard, expert

    @validator("player")
    def validate_player(cls, player):
        if player == 0:
            raise ValueError("Player must be 1 or -1")
        return player

    @validator("board")
    def validate_board_shape(cls, board):
        if len(board) != 8:
            raise ValueError("Board must have exactly 8 rows")
        for row in board:
            if len(row) != 8:
                raise ValueError("Each board row must have exactly 8 columns")
        return board
    
    @validator("difficulty")
    def validate_difficulty(cls, difficulty):
        valid_difficulties = ["easy", "medium", "hard", "expert"]
        if difficulty.lower() not in valid_difficulties:
            raise ValueError(f"Difficulty must be one of: {valid_difficulties}")
        return difficulty.lower()


# ---------- Routes ----------

@app.post("/move")
def move(req: MoveRequest):
    try:
        return make_move(req.board, req.player, req.row, req.col)
    except ValueError as e:
        # apply_move raises ValueError("Invalid move")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/ai-move")
def ai_move(req: AIMoveRequest):
    moves = get_valid_moves(req.board, req.player)

    if not moves:
        # Forced pass for AI: check whether opponent has moves.
        opponent = -req.player
        opponent_moves = get_valid_moves(req.board, opponent)

        # If opponent also has no moves -> game over
        if not opponent_moves:
            counts = count_discs(req.board)
            winner = None
            if counts[1] > counts[-1]:
                winner = 1
            elif counts[-1] > counts[1]:
                winner = -1

            logger.info("AI PASS: Game over, no moves available")
            return {
                "board": req.board,
                "next_player": None,
                "valid_moves": [],
                "game_over": True,
                "winner": winner,
                "move": None,
                "cache_info": {
                    "cache_hit": False,
                    "source": "game_over",
                    "depth": 0
                }
            }

        # Otherwise opponent gets to move (AI passes)
        logger.info("AI PASS: No moves, opponent continues")
        return {
            "board": req.board,
            "next_player": opponent,
            "valid_moves": [{"row": r, "col": c} for r, c in opponent_moves],
            "game_over": False,
            "winner": None,
            "move": None,
            "cache_info": {
                "cache_hit": False,
                "source": "pass",
                "depth": 0
            }
        }

    # Get AI move with cache information
    (row, col), cache_hit, depth = find_best_move_with_cache(req.board, req.player, req.difficulty)
    
    # Log cache status prominently
    cache_source = "DATABASE" if cache_hit else "FRESH_SEARCH"
    logger.info(f"AI MOVE: {cache_source} - Player {req.player} selected ({row},{col}) at depth {depth} using {req.difficulty} difficulty")

    try:
        result = make_move(req.board, req.player, row, col)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"AI produced invalid move: {e}")

    result["move"] = {"row": row, "col": col}
    result["cache_info"] = {
        "cache_hit": cache_hit,
        "source": cache_source,
        "depth": depth
    }
    
    return result

@app.post("/valid-moves")
def valid_moves(req: AIMoveRequest):
    moves = get_valid_moves(req.board, req.player)
    return {"valid_moves": [{"row": r, "col": c} for r, c in moves]}
