from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from core.game import make_move
from core.ai import find_best_move
from core.rules import get_valid_moves

app = FastAPI()

# ✅ CORS (Vite default is 5173)
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
    board: List[List[int]]
    player: int
    row: int
    col: int

class AIMoveRequest(BaseModel):
    board: List[List[int]]
    player: int


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
        # Forced pass for AI (we're not doing full game-over handling here yet)
        return {
            "board": req.board,
            "next_player": -req.player,
            "valid_moves": [{"row": r, "col": c} for r, c in get_valid_moves(req.board, -req.player)],
            "game_over": False,
            "winner": None,
            "move": None,
        }

    row, col = find_best_move(req.board, req.player)

    try:
        result = make_move(req.board, req.player, row, col)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"AI produced invalid move: {e}")

    result["move"] = {"row": row, "col": col}
    return result
