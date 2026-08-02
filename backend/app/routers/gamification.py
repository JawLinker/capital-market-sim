from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..i18n import get_lang, rival_name
from ..services.auth import get_current_player
from ..services import portfolio
from ..services.gamification import catalog

router = APIRouter(prefix="/api", tags=["gamification"])


@router.get("/achievements")
def get_achievements(request: Request, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    return catalog(db, player, get_lang(request))


@router.get("/leaderboard")
def get_leaderboard(request: Request, db: Session = Depends(get_db)):
    current_player = (
        get_current_player(db, request) or portfolio.get_or_create_player(db)
    )
    lang = get_lang(request)
    state = db.query(models.GameState).first()

    rivals = db.query(models.Rival).order_by(models.Rival.total_value.desc()).all()
    benchmark_value = 100_000.0 * state.benchmark_value / 100.0

    entries = []
    for rival in rivals:
        entries.append(
            {
                "id": rival.id,
                "name": rival.name,
                "kind": "rival",
                "strategy": rival.strategy,
                "value": round(rival.total_value, 2),
                "return_pct": round((rival.total_value / 100_000.0 - 1.0) * 100, 2),
                "rank": 0,
            }
        )
    entries.append(
        {
            "name": rival_name(lang, "Equal-Weight Benchmark"),
            "kind": "benchmark",
            "strategy": "index",
            "value": round(benchmark_value, 2),
            "return_pct": round((benchmark_value / 100_000.0 - 1.0) * 100, 2),
            "rank": 0,
        }
    )
    for player in db.query(models.Player).all():
        value = portfolio.portfolio_value(db, player)
        entries.append(
            {
                "id": player.id,
                "name": ("\u73a9\u5bb6 " + player.username) if lang == "zh" else player.name,
                "kind": "player",
                "strategy": "active",
                "value": round(value, 2),
                "return_pct": round((value / player.starting_cash - 1.0) * 100, 2),
                "rank": 0,
                "is_current": player.id == current_player.id,
            }
        )
    entries.sort(key=lambda e: -e["value"])
    for index, entry in enumerate(entries, start=1):
        entry["rank"] = index
    player_rank = next(
        e["rank"] for e in entries if e.get("is_current")
    )
    wins = sum(1 for entry in entries if entry["return_pct"] > 0.01)
    losses = sum(1 for entry in entries if entry["return_pct"] < -0.01)
    flat = len(entries) - wins - losses
    return {
        "entries": entries,
        "player_rank": player_rank,
        "total_entries": len(entries),
        "wins": wins,
        "flat": flat,
        "losses": losses,
    }
