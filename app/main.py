from fastapi import FastAPI, HTTPException
from app.schemas import MoveRequest, MoveResponse
from core.game import make_move, make_random_ai_move

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Othello Backend",
    description="FastAPI backend for Othello AI",
    version="0.1.0"
)


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



@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/move", response_model=MoveResponse)
def move(request: MoveRequest):
    try:
        if request.use_ai:
            return make_random_ai_move(
                request.board,
                request.player
            )

        if request.row is None or request.col is None:
            raise HTTPException(
                status_code=400,
                detail="Row and col required for human move"
            )

        return make_move(
            request.board,
            request.player,
            request.row,
            request.col
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
