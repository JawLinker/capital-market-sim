from datetime import UTC, datetime

from sqlalchemy.orm import Session

from .. import models
from ..i18n import achievement_text


def _unlock(db: Session, player: models.Player, code: str) -> bool:
    achievement = db.query(models.Achievement).filter(models.Achievement.code == code).first()
    if achievement is None:
        return False
    exists = (
        db.query(models.UnlockedAchievement)
        .filter(
            models.UnlockedAchievement.player_id == player.id,
            models.UnlockedAchievement.achievement_id == achievement.id,
        )
        .first()
    )
    if exists:
        return False
    db.add(
        models.UnlockedAchievement(
            player_id=player.id,
            achievement_id=achievement.id,
            unlocked_at=datetime.now(UTC).isoformat(timespec="seconds"),
        )
    )
    return True


def check_all(db: Session, player: models.Player) -> list[str]:
    state = db.query(models.GameState).first()
    holdings = db.query(models.Holding).filter(models.Holding.player_id == player.id).all()
    transactions = (
        db.query(models.Transaction)
        .filter(models.Transaction.player_id == player.id)
        .all()
    )
    history = (
        db.query(models.PortfolioHistory)
        .filter(models.PortfolioHistory.player_id == player.id)
        .order_by(models.PortfolioHistory.day)
        .all()
    )
    value = player.cash + sum(
        holding.shares * db.get(models.Stock, holding.stock_id).price for holding in holdings
    )

    unlocked: list[str] = []

    def check(code: str, predicate: bool) -> None:
        if predicate and _unlock(db, player, code):
            unlocked.append(code)

    buy_count = sum(1 for t in transactions if t.action == "buy")
    sell_count = sum(1 for t in transactions if t.action == "sell")
    industries = {db.get(models.Stock, h.stock_id).industry for h in holdings}

    check("first_trade", buy_count >= 1)
    check("first_sell", sell_count >= 1)
    check("trade_10", len(transactions) >= 10)
    check("trade_50", len(transactions) >= 50)
    check("trade_100", len(transactions) >= 100)
    check("five_sectors", len(industries) >= 5)
    check(
        "concentrated",
        any(
            holding.shares * db.get(models.Stock, holding.stock_id).price >= value * 0.6
            and value > 0
            for holding in holdings
        ),
    )
    check("cash_king", state.day >= 20 and player.cash >= value * 0.7 and value > 0)

    from .advisor import portfolio_report

    report = portfolio_report(db, player)
    check(
        "value_finder",
        any(h["dimensions"]["valuation"]["label"] == "Undervalued" for h in report["holdings"]),
    )
    check(
        "momentum_rider",
        any(
            db.get(models.Stock, h.stock_id).momentum_20d and db.get(models.Stock, h.stock_id).momentum_20d > 0.10
            for h in holdings
        ),
    )

    bear_days = 0
    if state.market_cycle == "bear":
        bear_days = min(state.day, 5)
    check("bear_survivor", bear_days >= 5)

    if len(history) >= 2:
        prev = history[-2].value
        change = (value - prev) / prev if prev else 0.0
        check("green_day", change > 0.015)
        check("red_day", change < -0.02)

    check("milestone_110k", value >= 110_000)
    check("milestone_150k", value >= 150_000)
    check("milestone_200k", value >= 200_000)
    check("day_30", state.day >= 30)
    check("day_100", state.day >= 100)

    try:
        from .chronicle import build_chronicle

        chronicle = build_chronicle(db, player, state.date, "en")
        current = next(
            (beat for beat in chronicle["beats"] if beat["status"] == "current"),
            None,
        )
        if current and current.get("objective") and current["objective"]["met"]:
            kind = current["objective"]["type"]
            code_by_kind = {
                "tech_exposure": "chronicle_tech",
                "tech_holdings": "chronicle_tech",
                "tech_return": "chronicle_profit",
                "cash_ratio": "chronicle_cash",
                "total_return": "chronicle_survivor",
            }
            if kind in code_by_kind:
                check(code_by_kind[kind], True)
    except Exception:
        pass

    db.commit()
    return unlocked


def catalog(db: Session, player: models.Player, lang: str = "en") -> dict:
    achievements = db.query(models.Achievement).order_by(models.Achievement.id).all()
    unlocked_rows = {
        row.achievement_id
        for row in db.query(models.UnlockedAchievement)
        .filter(models.UnlockedAchievement.player_id == player.id)
        .all()
    }
    items = []
    for a in achievements:
        title, description = achievement_text(lang, a.code, a.title, a.description)
        items.append(
            {
            "code": a.code,
            "title": title,
            "description": description,
            "category": a.category,
            "unlocked": a.id in unlocked_rows,
            }
        )

    holdings = db.query(models.Holding).filter(models.Holding.player_id == player.id).all()
    value = player.cash + sum(
        holding.shares * db.get(models.Stock, holding.stock_id).price for holding in holdings
    )
    milestones = [
        {"threshold": 110_000, "label": "¥110k"},
        {"threshold": 125_000, "label": "¥125k"},
        {"threshold": 150_000, "label": "¥150k"},
        {"threshold": 200_000, "label": "¥200k"},
        {"threshold": 300_000, "label": "¥300k"},
    ]
    for milestone in milestones:
        prev_threshold = milestone["threshold"] / 1.1
        progress = (value - prev_threshold) / (milestone["threshold"] - prev_threshold)
        milestone["progress"] = max(0.0, min(1.0, progress))
        milestone["reached"] = value >= milestone["threshold"]

    return {
        "achievements": items,
        "milestones": milestones,
        "portfolio_value": round(value, 2),
        "unlocked_count": sum(1 for item in items if item["unlocked"]),
        "total_count": len(items),
    }
