import random

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
from ..services.blackswan import (
    black_swan_options,
    localize_black_swan,
    pick_black_swan,
)
from ..services.decisions import create_black_swan_decision
from ..services.duels import settle_duels
from ..services.pending_orders import execute_pending_orders

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
    execute_pending_orders(db)
    duel_results = settle_duels(db)
    black_swan = None
    if days == 1 and random.random() < 0.03:
        state = db.query(models.GameState).first()
        event = pick_black_swan(state.date if state else result["date"])
        if event is not None:
            state.sentiment = max(0.05, min(1.0, state.sentiment + event["sentiment_delta"]))
            db.add(
                models.NewsEvent(
                    day=result["day"],
                    headline=event["title_zh"] if get_lang(request) == "zh" else event["title_en"],
                    summary=(
                        event["prose_zh"] if get_lang(request) == "zh" else event["prose_en"]
                    ),
                    category="market",
                    scope="market",
                    kind="blackswan",
                    impact_pct=round(event["sentiment_delta"] * 100, 2),
                )
            )
            db.commit()
            lang = get_lang(request)
            black_swan = localize_black_swan({**event, "date": state.date}, lang)
            decision = create_black_swan_decision(
                db,
                player,
                event,
                lang,
                result["day"],
            )
            db.commit()
            black_swan["decision_id"] = decision.id
            black_swan["options"] = [
                {
                    "key": option["key"],
                    "label": option["label"],
                    "detail": option["detail"],
                }
                for option in black_swan_options(lang)
            ]
    unlocked = check_all(db, player)
    summary = portfolio.portfolio_summary(db, player)
    return {
        "result": result,
        "days_advanced": days,
        "unlocked_achievements": unlocked,
        "portfolio": summary,
        "black_swan": black_swan,
        "duel_results": duel_results,
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
    guest_ids = [
        row.id
        for row in db.query(models.Player)
        .filter(models.Player.is_host != 1)
        .all()
    ]
    if guest_ids:
        for table in (
            models.UnlockedAchievement,
            models.PortfolioHistory,
            models.Transaction,
            models.Holding,
            models.RankStreak,
            models.StorylineProgress,
            models.PendingOrder,
            models.Duel,
            models.Decision,
        ):
            db.query(table).filter(table.player_id.in_(guest_ids)).delete(
                synchronize_session=False
            )
        db.query(models.Player).filter(models.Player.is_host != 1).delete(
            synchronize_session=False
        )
    for table in (
        models.PortfolioHistory,
        models.Transaction,
        models.Holding,
        models.PendingOrder,
        models.Duel,
        models.Decision,
    ):
        db.query(table).filter(table.player_id == player.id).delete(
            synchronize_session=False
        )
    for table in (
        models.NewsEvent,
        models.PriceHistory,
        models.BotTrade,
        models.BotHistory,
        models.BotHolding,
        models.Rival,
        models.Stock,
        models.GameState,
    ):
        db.query(table).delete(synchronize_session=False)
    db.commit()
    from ..seed import seed_database

    seed_database(db)
    host = db.query(models.Player).filter(models.Player.is_host == 1).first()
    if host is not None:
        streak = (
            db.query(models.RankStreak)
            .filter(models.RankStreak.player_id == host.id)
            .first()
        )
        if streak is not None:
            streak.current_streak = 0
            streak.last_day = -1
            db.commit()
    return {"status": "reset", "day": 0}
