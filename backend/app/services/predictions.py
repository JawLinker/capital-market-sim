"""Judgment tags on stocks, validated by the market with a seer streak."""

from sqlalchemy.orm import Session

from .. import models

VALID_THESES = {"rally", "dip", "gamble", "value"}


def create_judgment(
    db: Session,
    player: models.Player,
    stock: models.Stock,
    thesis: str,
    day: int,
) -> models.Judgment:
    if thesis not in VALID_THESES:
        raise ValueError("Unknown judgment thesis")
    existing = (
        db.query(models.Judgment)
        .filter(
            models.Judgment.player_id == player.id,
            models.Judgment.stock_id == stock.id,
            models.Judgment.status == "open",
        )
        .first()
    )
    if existing is not None:
        raise ValueError("You already have an open judgment on this stock")
    judgment = models.Judgment(
        player_id=player.id,
        stock_id=stock.id,
        thesis=thesis,
        buy_price=round(stock.price, 4),
        buy_day=day,
    )
    db.add(judgment)
    db.commit()
    return judgment


def list_judgments(db: Session, player: models.Player) -> list:
    rows = (
        db.query(models.Judgment, models.Stock)
        .join(models.Stock, models.Judgment.stock_id == models.Stock.id)
        .filter(models.Judgment.player_id == player.id)
        .order_by(models.Judgment.id.desc())
        .all()
    )
    return [
        {
            "id": judgment.id,
            "ticker": stock.ticker,
            "name": stock.name,
            "thesis": judgment.thesis,
            "buy_price": judgment.buy_price,
            "buy_day": judgment.buy_day,
            "status": judgment.status,
            "return_pct": judgment.return_pct,
        }
        for judgment, stock in rows
    ]


def validate_judgments(db: Session) -> list:
    state = db.query(models.GameState).first()
    open_judgments = (
        db.query(models.Judgment)
        .filter(models.Judgment.status == "open")
        .all()
    )
    results = []
    player_results = {}
    for judgment in open_judgments:
        stock = db.get(models.Stock, judgment.stock_id)
        if stock is None:
            judgment.status = "wrong"
            continue
        ret = stock.price / judgment.buy_price - 1.0
        if ret >= 0.005:
            judgment.status = "right"
            judgment.return_pct = round(ret * 100, 2)
        elif ret <= -0.005:
            judgment.status = "wrong"
            judgment.return_pct = round(ret * 100, 2)
        else:
            continue
        judgment.resolved_day = state.day
        item = {
            "player_id": judgment.player_id,
            "judgment_id": judgment.id,
            "name": stock.name,
            "thesis": judgment.thesis,
            "status": judgment.status,
            "return_pct": judgment.return_pct,
        }
        results.append(item)
        player_results.setdefault(judgment.player_id, []).append(item)

    for player_id, items in player_results.items():
        streak = (
            db.query(models.PredictionStreak)
            .filter(models.PredictionStreak.player_id == player_id)
            .first()
        )
        if streak is None:
            streak = models.PredictionStreak(
                player_id=player_id,
                current_streak=0,
                best_streak=0,
            )
            db.add(streak)
        for item in items:
            streak.current_streak = (
                streak.current_streak + 1
                if item["status"] == "right"
                else 0
            )
            streak.best_streak = max(streak.best_streak, streak.current_streak)
    db.commit()
    return results
