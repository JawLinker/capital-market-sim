from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..i18n import company_name, get_lang, rival_name

router = APIRouter(prefix="/api", tags=["bots"])


@router.get("/bots/{bot_id}")
def get_bot(
    bot_id: int,
    request: Request,
    limit: int = Query(default=120, le=500),
    db: Session = Depends(get_db),
):
    lang = get_lang(request)
    bot = db.get(models.Rival, bot_id)
    if bot is None:
        raise HTTPException(status_code=404, detail="Bot not found")

    positions = (
        db.query(models.BotHolding)
        .filter(models.BotHolding.bot_id == bot_id)
        .count()
    )
    history = (
        db.query(models.BotHistory)
        .filter(models.BotHistory.bot_id == bot_id)
        .order_by(models.BotHistory.day)
        .all()
    )
    trades = (
        db.query(models.BotTrade)
        .filter(models.BotTrade.bot_id == bot_id)
        .order_by(models.BotTrade.id.desc())
        .limit(limit)
        .all()
    )
    return {
        "id": bot.id,
        "name": rival_name(lang, bot.name),
        "strategy": bot.strategy,
        "cash": round(bot.cash, 2),
        "invested": round(bot.invested_value, 2),
        "value": round(bot.total_value, 2),
        "return_pct": round((bot.total_value / 100_000.0 - 1.0) * 100, 2),
        "positions": positions,
        "equity": [
            {
                "day": row.day,
                "value": row.value,
                "cash": row.cash,
                "invested": row.invested,
            }
            for row in history
        ],
        "trades": [
            {
                "id": trade.id,
                "day": trade.day,
                "ticker": db.get(models.Stock, trade.stock_id).ticker,
                "name": company_name(
                    lang,
                    db.get(models.Stock, trade.stock_id).ticker,
                    db.get(models.Stock, trade.stock_id).name,
                ),
                "action": trade.action,
                "shares": trade.shares,
                "price": trade.price,
                "notional": trade.notional,
            }
            for trade in trades
        ],
    }


@router.get("/bots")
def list_bots(
    request: Request,
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db),
):
    lang = get_lang(request)
    bots = db.query(models.Rival).all()
    holdings_count = defaultdict(int)
    for row in db.query(models.BotHolding).all():
        holdings_count[row.bot_id] += 1

    trades = (
        db.query(models.BotTrade)
        .order_by(models.BotTrade.id.desc())
        .limit(limit)
        .all()
    )
    recent_trades = []
    latest_day = None
    day_flow: dict[int, float] = defaultdict(float)
    for trade in trades:
        bot = db.get(models.Rival, trade.bot_id)
        stock = db.get(models.Stock, trade.stock_id)
        if latest_day is None:
            latest_day = trade.day
        if trade.day == latest_day:
            day_flow[trade.stock_id] += (
                trade.notional if trade.action == "buy" else -trade.notional
            )
        recent_trades.append(
            {
                "id": trade.id,
                "day": trade.day,
                "bot": rival_name(lang, bot.name),
                "strategy": bot.strategy,
                "ticker": stock.ticker,
                "name": company_name(lang, stock.ticker, stock.name),
                "action": trade.action,
                "shares": trade.shares,
                "price": trade.price,
                "notional": trade.notional,
            }
        )

    net_flow = []
    for stock_id, net in day_flow.items():
        stock = db.get(models.Stock, stock_id)
        net_flow.append(
            {
                "ticker": stock.ticker,
                "name": company_name(lang, stock.ticker, stock.name),
                "net": round(net, 2),
            }
        )
    net_flow.sort(key=lambda item: -abs(item["net"]))

    return {
        "bots": [
            {
                "id": bot.id,
                "name": rival_name(lang, bot.name),
                "strategy": bot.strategy,
                "cash": round(bot.cash, 2),
                "invested": round(bot.invested_value, 2),
                "value": round(bot.total_value, 2),
                "positions": holdings_count.get(bot.id, 0),
            }
            for bot in bots
        ],
        "recent_trades": recent_trades,
        "net_flow": net_flow,
        "latest_day": latest_day,
    }
