from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..i18n import company_name, get_lang
from ..services import portfolio
from ..services.auth import get_current_player

router = APIRouter(prefix="/api", tags=["replay"])


@router.get("/replay")
def get_replay(request: Request, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    lang = get_lang(request)
    history = (
        db.query(models.PortfolioHistory)
        .filter(models.PortfolioHistory.player_id == player.id)
        .order_by(models.PortfolioHistory.day)
        .all()
    )
    date_by_day = {row.day: row.date for row in history}
    trades = (
        db.query(models.Transaction)
        .filter(models.Transaction.player_id == player.id)
        .order_by(models.Transaction.day)
        .all()
    )
    trade_rows = []
    for trade in trades:
        stock = db.get(models.Stock, trade.stock_id)
        trade_rows.append(
            {
                "id": trade.id,
                "day": trade.day,
                "date": date_by_day.get(trade.day),
                "ticker": stock.ticker if stock else "",
                "name": company_name(lang, stock.ticker, stock.name) if stock else "",
                "action": trade.action,
                "shares": trade.shares,
                "price": trade.price,
                "gross": trade.gross,
                "realized_pnl": trade.realized_pnl,
            }
        )

    realized = [trade.realized_pnl for trade in trades if trade.realized_pnl]
    wins = sum(1 for value in realized if value > 0)
    losses = sum(1 for value in realized if value < 0)
    total_realized = sum(realized)
    best = max(realized) if realized else 0.0
    worst = min(realized) if realized else 0.0

    max_drawdown = 0.0
    peak = None
    for row in history:
        if peak is None or row.value > peak:
            peak = row.value
        if peak and peak > 0:
            max_drawdown = max(max_drawdown, (peak - row.value) / peak)

    total_value = portfolio.portfolio_value(db, player)
    final_return = (total_value / player.starting_cash - 1.0) * 100 if player.starting_cash else 0.0
    return {
        "stats": {
            "total_trades": len(trade_rows),
            "wins": wins,
            "losses": losses,
            "flat": len(trade_rows) - wins - losses,
            "win_rate": round((wins / len(trade_rows) * 100), 2) if trade_rows else 0.0,
            "total_realized": round(total_realized, 2),
            "best_trade": round(best, 2),
            "worst_trade": round(worst, 2),
            "max_drawdown": round(max_drawdown * 100, 2),
            "final_return": round(final_return, 2),
        },
        "trades": trade_rows,
    }
