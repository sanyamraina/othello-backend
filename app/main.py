from fastapi import FastAPI, HTTPException
from app.schemas import MoveRequest, MoveResponse
from core.game import make_move

app = FastAPI(
    title="Othello Backend",
    description="FastAPI backend for Othello AI",
    version="0.1.0"
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/move", response_model=MoveResponse)
def move(request: MoveRequest):
    if request.use_ai:
        raise HTTPException(status_code=501, detail="AI not implemented yet")

    if request.row is None or request.col is None:
        raise HTTPException(status_code=400, detail="Row and col required for human move")

    try:
        result = make_move(
            request.board,
            request.player,
            request.row,
            request.col
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
