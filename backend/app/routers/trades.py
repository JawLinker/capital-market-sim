from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import TradeRequest
from ..i18n import get_lang
from ..services.auth import get_current_player
from ..services import portfolio
from ..services.gamification import check_all

router = APIRouter(prefix="/api", tags=["trades"])


@router.post("/trades")
def create_trade(request: Request, body: TradeRequest, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    stock = (
        db.query(models.Stock)
        .filter(models.Stock.ticker == body.ticker.upper())
        .first()
    )
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    try:
        trade = portfolio.execute_trade(
        db,
        player,
        stock,
        body.action,
        body.shares,
        body.dark_pool,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    unlocked = check_all(db, player)
    return {
        "trade": trade,
        "unlocked_achievements": unlocked,
        "portfolio": portfolio.portfolio_summary(db, player),
    }


@router.get("/transactions")
def get_transactions(
    request: Request,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    return {
        "transactions": portfolio.transaction_history(db, player, limit, get_lang(request))
    }
