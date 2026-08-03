from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..services import portfolio
from ..services.auth import get_current_player
from ..services.predictions import create_judgment, list_judgments

router = APIRouter(prefix="/api", tags=["predictions"])


class JudgmentRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=8)
    thesis: str = Field(min_length=1, max_length=16)


@router.post("/judgments")
def add_judgment(request: Request, body: JudgmentRequest, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    stock = (
        db.query(models.Stock)
        .filter(models.Stock.ticker == body.ticker.upper())
        .first()
    )
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    state = db.query(models.GameState).first()
    try:
        judgment = create_judgment(db, player, stock, body.thesis, state.day)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"judgment": {"id": judgment.id, "ticker": stock.ticker, "thesis": judgment.thesis}}


@router.get("/judgments")
def get_judgments(request: Request, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    return {"judgments": list_judgments(db, player)}
