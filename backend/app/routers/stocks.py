from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..i18n import company_name, get_lang
from ..services.orderbook import is_limit_down, is_limit_up
from ..services.replay import index_series
from ..services.intraday import intraday_price

router = APIRouter(prefix="/api", tags=["stocks"])


@router.get("/index/history")
def get_index_history(
    limit: int = Query(default=510, ge=30, le=1800),
):
    rows = index_series()
    selected = rows[-limit:]
    return {
        "name": "Shanghai Composite",
        "series": [
            {
                "date": row["d"],
                "open": row["o"],
                "high": row["h"],
                "low": row["l"],
                "close": row["c"],
                "volume": row["v"],
            }
            for row in selected
        ],
    }


def _quote_dict(
    stock: models.Stock,
    latest: models.PriceHistory | None,
    lang: str = "en",
    bot_net_flow: float = 0.0,
) -> dict:
    change = stock.price - stock.prev_close
    change_pct = (change / stock.prev_close * 100) if stock.prev_close else 0.0
    return {
        "ticker": stock.ticker,
        "name": company_name(lang, stock.ticker, stock.name),
        "industry": stock.industry,
        "price": round(stock.price, 2),
        "prev_close": round(stock.prev_close, 2),
        "change": round(change, 2),
        "change_pct": round(change_pct, 2),
        "open": round(latest.open, 2) if latest else round(stock.prev_close, 2),
        "high": round(latest.high, 2) if latest else round(stock.price, 2),
        "low": round(latest.low, 2) if latest else round(stock.price, 2),
        "volume": stock.volume,
        "avg_volume": stock.avg_volume,
        "volatility": round(stock.volatility, 4),
        "market_cap": round(stock.market_cap, 0),
        "pe_ratio": round(stock.pe_ratio, 2),
        "beta": round(stock.beta, 2),
        "fifty_two_week_high": stock.fifty_two_week_high,
        "fifty_two_week_low": stock.fifty_two_week_low,
        "momentum_20d": round(stock.momentum_20d or 0.0, 6),
        "momentum_60d": round(stock.momentum_60d or 0.0, 6),
        "eps_estimate": round(stock.eps_estimate, 4),
        "eps_actual": round(stock.eps_actual, 4),
        "earnings_growth": round(stock.earnings_growth, 4),
        "next_earnings_day": stock.next_earnings_day,
        "last_surprise_pct": round(stock.last_surprise_pct, 2),
        "bot_net_flow": round(bot_net_flow, 2),
        "player_impact": round(stock.player_impact or 0.0, 6),
        "bid": stock.bid,
        "ask": stock.ask,
        "bid_depth": stock.bid_depth,
        "ask_depth": stock.ask_depth,
        "limit_pct": stock.limit_pct,
        "limit_up": is_limit_up(stock),
        "limit_down": is_limit_down(stock),
    }


@router.get("/stocks")
def list_stocks(
    request: Request,
    industry: str | None = Query(default=None),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(models.Stock)
    if industry and industry != "all":
        query = query.filter(models.Stock.industry == industry)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            models.Stock.ticker.ilike(pattern) | models.Stock.name.ilike(pattern)
        )
    stocks = query.order_by(models.Stock.ticker).all()
    latest_rows = {
        row.stock_id: row
        for row in db.query(models.PriceHistory)
        .filter(
            models.PriceHistory.trade_date
            == db.query(models.GameState).first().date
        )
        .all()
    }
    lang = get_lang(request)
    return {"stocks": [_quote_dict(s, latest_rows.get(s.id), lang) for s in stocks]}


@router.get("/stocks/{ticker}")
def get_stock(request: Request, ticker: str, db: Session = Depends(get_db)):
    stock = db.query(models.Stock).filter(models.Stock.ticker == ticker.upper()).first()
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    latest = (
        db.query(models.PriceHistory)
        .filter(models.PriceHistory.stock_id == stock.id)
        .order_by(models.PriceHistory.trade_date.desc())
        .first()
    )
    latest_day = db.query(func.max(models.BotTrade.day)).scalar()
    net_flow = 0.0
    if latest_day is not None:
        for trade in (
            db.query(models.BotTrade)
            .filter(
                models.BotTrade.day == latest_day,
                models.BotTrade.stock_id == stock.id,
            )
            .all()
        ):
            net_flow += trade.notional if trade.action == "buy" else -trade.notional
    return _quote_dict(stock, latest, get_lang(request), net_flow)


@router.get("/stocks/{ticker}/history")
def get_history(
    ticker: str,
    limit: int = Query(default=252, ge=30, le=510),
    db: Session = Depends(get_db),
):
    stock = db.query(models.Stock).filter(models.Stock.ticker == ticker.upper()).first()
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    rows = (
        db.query(models.PriceHistory)
        .filter(models.PriceHistory.stock_id == stock.id)
        .order_by(models.PriceHistory.trade_date.desc())
        .limit(limit)
        .all()
    )
    series = [
        {
            "date": row.trade_date,
            "open": row.open,
            "high": row.high,
            "low": row.low,
            "close": row.close,
            "volume": row.volume,
        }
        for row in reversed(rows)
    ]
    return {"ticker": stock.ticker, "series": series}


@router.get("/stocks/{ticker}/intraday")
def get_intraday(
    ticker: str,
    elapsed: float = 0,
    window: float = 120,
    db: Session = Depends(get_db),
):
    stock = (
        db.query(models.Stock)
        .filter(models.Stock.ticker == ticker.upper())
        .first()
    )
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    state = db.query(models.GameState).first()
    price = intraday_price(stock, state.day if state else 0, elapsed, window)
    return {
        "ticker": stock.ticker,
        "base": round(stock.price, 2),
        "price": price,
        "change_pct": round((price / stock.prev_close - 1.0) * 100, 2)
        if stock.prev_close
        else 0.0,
    }
