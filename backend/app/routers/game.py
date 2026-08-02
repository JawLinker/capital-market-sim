from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models
from ..i18n import company_name, get_lang
from ..schemas import AdvanceRequest
from ..services.auth import get_current_player
from ..services import portfolio
from ..services.gamification import check_all
from ..services.market_engine import advance_day
from ..i18n import get_lang

router = APIRouter(prefix="/api", tags=["game"])


def _market_overview(db: Session, lang: str = "en"):
    state = db.query(models.GameState).first()
    stocks = db.query(models.Stock).all()
    movers = sorted(
        stocks,
        key=lambda s: (s.price / s.prev_close - 1.0) if s.prev_close else 0.0,
        reverse=True,
    )
    return {
        "day": state.day,
        "date": state.date,
        "market_cycle": state.market_cycle,
        "sentiment": round(state.sentiment, 3),
        "policy_rate": state.policy_rate,
        "inflation": round(state.inflation, 2),
        "style_factor": round(state.style_factor, 4),
        "shanghai_index": state.shanghai_index,
        "shanghai_change_pct": round(
            (state.shanghai_index / state.shanghai_prev - 1.0) * 100, 2
        )
        if state.shanghai_prev
        else 0.0,
        "benchmark_value": state.benchmark_value,
        "benchmark_change_pct": round(
            (state.benchmark_value / state.benchmark_prev - 1.0) * 100, 3
        )
        if state.benchmark_prev
        else 0.0,
        "gainers": [
            {
                "ticker": s.ticker,
                "name": company_name(lang, s.ticker, s.name),
                "price": s.price,
                "change_pct": round((s.price / s.prev_close - 1.0) * 100, 2),
            }
            for s in movers[:5]
        ],
        "losers": [
            {
                "ticker": s.ticker,
                "name": company_name(lang, s.ticker, s.name),
                "price": s.price,
                "change_pct": round((s.price / s.prev_close - 1.0) * 100, 2),
            }
            for s in reversed(movers[-5:])
        ],
    }


@router.get("/state")
def get_state(request: Request, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    summary = portfolio.portfolio_summary(db, player)
    overview = _market_overview(db, get_lang(request))
    return {"portfolio": summary, "market": overview}


@router.post("/game/advance")
def post_advance(
    request: Request,
    body: AdvanceRequest | None = None,
    db: Session = Depends(get_db),
):
    days = body.days if body else 1
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    if not player.is_host:
        detail = (
            "只有房主可以推进时间"
            if get_lang(request) == "zh"
            else "Only the host can advance time"
        )
        raise HTTPException(status_code=403, detail=detail)
    result = None
    for _ in range(days):
        result = advance_day(db)
    unlocked = check_all(db, player)
    summary = portfolio.portfolio_summary(db, player)
    return {
        "result": result,
        "days_advanced": days,
        "unlocked_achievements": unlocked,
        "portfolio": summary,
    }


@router.post("/game/reset")
def post_reset(request: Request, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    if not player.is_host:
        detail = (
            "只有房主可以重置游戏"
            if get_lang(request) == "zh"
            else "Only the host can reset the game"
        )
        raise HTTPException(status_code=403, detail=detail)
    for table in (
        models.UnlockedAchievement,
        models.PortfolioHistory,
        models.Transaction,
        models.Holding,
        models.NewsEvent,
        models.PriceHistory,
        models.BotTrade,
        models.BotHistory,
        models.BotHolding,
        models.Rival,
        models.Achievement,
        models.Player,
        models.Stock,
        models.GameState,
    ):
        db.query(table).delete()
    db.commit()
    from ..seed import seed_database

    seed_database(db)
    return {"status": "reset", "day": 0}
