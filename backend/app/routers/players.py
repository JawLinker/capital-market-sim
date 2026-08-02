from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..i18n import company_name, get_lang
from ..services.auth import get_current_player

router = APIRouter(prefix="/api/players", tags=["players"])


@router.get("/activity")
def player_activity(
    request: Request,
    limit: int = Query(default=30, le=100),
    db: Session = Depends(get_db),
):
    """Recent executions from every player, newest first."""
    lang = get_lang(request)
    current = get_current_player(db, request)
    players = {player.id: player for player in db.query(models.Player).all()}
    rows = (
        db.query(models.Transaction)
        .order_by(models.Transaction.id.desc())
        .limit(limit)
        .all()
    )
    trades = []
    for row in rows:
        player = players.get(row.player_id)
        stock = db.get(models.Stock, row.stock_id)
        if player is None or stock is None:
            continue
        trades.append(
            {
                "id": row.id,
                "player_id": player.id,
                "player": player.username or player.name,
                "is_current": bool(
                    current is not None and player.id == current.id
                ),
                "ticker": stock.ticker,
                "name": company_name(lang, stock.ticker, stock.name),
                "action": row.action,
                "shares": row.shares,
                "price": row.price,
                "gross": row.gross,
                "day": row.day,
            }
        )
    return {"trades": trades}
