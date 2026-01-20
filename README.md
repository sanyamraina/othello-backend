# Othello Backend

A FastAPI rules engine for Othello that validates moves, applies flips, and provides a simple AI move. Designed to be consumed by the React frontend.

## Features
- Legal move validation and board updates
- Forced pass handling and game-over detection
- Random-move AI (baseline opponent)
- Clean JSON API for move generation

## Prerequisites
- Python 3.9+

## Setup
```bash
cd othello-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Server starts at `http://127.0.0.1:8000`.

FastAPI docs: `http://127.0.0.1:8000/docs`.

## Board Encoding
- `1` = Black
- `-1` = White
- `0` = Empty

## API
All endpoints are `POST` and accept JSON.

### `/move`
Apply a player move and return the updated board.
```json
{
  "board": [[0,0,0,0,0,0,0,0], ...],
  "player": 1,
  "row": 2,
  "col": 3
}
```

### `/ai-move`
Request a move from the AI for the given position.
```json
{
  "board": [[0,0,0,0,0,0,0,0], ...],
  "player": -1
}
```

### `/valid-moves`
Fetch valid moves for a player without applying one.
```json
{
  "board": [[0,0,0,0,0,0,0,0], ...],
  "player": 1
}
```

## Testing
```bash
cd othello-backend
pytest
```
