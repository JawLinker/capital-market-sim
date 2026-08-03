"""Player choices with consequences for black swans and era transitions."""

import json

from sqlalchemy.orm import Session

from .. import models
from .blackswan import black_swan_options

ERA_BONUS_CASH = {
    "gold": [5000, 8000, 10000],
    "silver": [2000, 3000, 4000],
    "bronze": [500, 1000, 1500],
    "dark": [300, 600, 1000],
}


def create_black_swan_decision(
    db: Session,
    player: models.Player,
    event: dict,
    lang: str,
    day: int,
) -> models.Decision:
    decision = models.Decision(
        player_id=player.id,
        kind="blackswan",
        payload=json.dumps(
            {
                "title": event["title_zh"] if lang == "zh" else event["title_en"],
                "options": black_swan_options(lang),
            },
            ensure_ascii=False,
        ),
        created_day=day,
    )
    db.add(decision)
    db.flush()
    return decision


def resolve_decision(
    db: Session,
    player: models.Player,
    decision_id: int,
    option_key: str,
) -> dict:
    decision = (
        db.query(models.Decision)
        .filter(
            models.Decision.id == decision_id,
            models.Decision.player_id == player.id,
            models.Decision.status == "open",
        )
        .first()
    )
    if decision is None:
        raise ValueError("Open decision not found")
    payload = json.loads(decision.payload)
    option = next(
        (item for item in payload.get("options", []) if item["key"] == option_key),
        None,
    )
    if option is None:
        raise ValueError("Invalid decision option")
    effect = option["effect"]
    cash_delta = round(effect.get("cash", 0), 2)
    sentiment_delta = round(effect.get("sentiment", 0), 4)
    state = db.query(models.GameState).first()
    if cash_delta:
        player.cash = round(player.cash + cash_delta, 2)
    if sentiment_delta and state is not None:
        state.sentiment = max(0.05, min(1.0, state.sentiment + sentiment_delta))
    decision.status = "resolved"
    db.commit()
    return {
        "decision_id": decision.id,
        "option": option_key,
        "cash_delta": cash_delta,
        "sentiment_delta": sentiment_delta,
    }


def apply_era_bonus(
    db: Session,
    player: models.Player,
    grade_key: str,
    option_key: str,
) -> dict:
    if grade_key not in ERA_BONUS_CASH:
        raise ValueError("Invalid era grade")
    cash_delta = 0
    sentiment_delta = 0
    if option_key == "sentiment":
        sentiment_delta = 0.05
    elif option_key in {"cash_small", "cash_mid", "cash_large"}:
        index = {"cash_small": 0, "cash_mid": 1, "cash_large": 2}[option_key]
        cash_delta = round(ERA_BONUS_CASH[grade_key][index], 2)
    else:
        raise ValueError("Invalid era bonus option")
    state = db.query(models.GameState).first()
    if cash_delta:
        player.cash = round(player.cash + cash_delta, 2)
    if sentiment_delta and state is not None:
        state.sentiment = max(0.05, min(1.0, state.sentiment + sentiment_delta))
    db.commit()
    return {
        "cash_delta": cash_delta,
        "sentiment_delta": sentiment_delta,
    }
