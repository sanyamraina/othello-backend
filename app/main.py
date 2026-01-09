from fastapi import FastAPI, HTTPException
from app.schemas import MoveRequest, MoveResponse

app = FastAPI(
    title="Othello Backend",
    description="FastAPI backend for Othello AI",
    version="0.1.0"
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/move", response_model=MoveResponse)
def make_move(request: MoveRequest):
    # TEMPORARY STUB — real logic comes next
    raise HTTPException(status_code=501, detail="Move logic not implemented yet")
