"""Annual cash dividends: shareholders get paid and the price ex-dividends."""

from sqlalchemy.orm import Session

from .. import models


def _dividend_date(stock_id: int, year: int) -> str:
    month = 6 + stock_id % 3
    day = 10 + (stock_id * 3) % 15
    return f"{year}-{month:02d}-{day:02d}"


def process_dividends(db: Session) -> list:
    state = db.query(models.GameState).first()
    if state is None or not state.date:
        return []
    year = int(state.date[:4])
    results = []
    for stock in db.query(models.Stock).all():
        if _dividend_date(stock.id, year) != state.date or stock.price <= 0:
            continue
        yield_pct = 0.8 + (stock.id % 11) * 0.4
        per_share = round(stock.price * yield_pct / 100, 4)
        if per_share <= 0:
            continue
        impact = round(-per_share / stock.price * 100, 2)
        stock.price = round(max(0.01, stock.price - per_share), 2)
        for holding in (
            db.query(models.Holding)
            .filter(models.Holding.stock_id == stock.id)
            .all()
        ):
            player = db.get(models.Player, holding.player_id)
            total = round(holding.shares * per_share, 2)
            player.cash = round(player.cash + total, 2)
            results.append(
                {
                    "player_id": player.id,
                    "name": stock.name,
                    "per_share": per_share,
                    "shares": holding.shares,
                    "total": total,
                }
            )
        for bot_holding in (
            db.query(models.BotHolding)
            .filter(models.BotHolding.stock_id == stock.id)
            .all()
        ):
            bot = db.get(models.Rival, bot_holding.bot_id)
            if bot is not None:
                add = round(bot_holding.shares * per_share, 2)
                bot.cash = round(bot.cash + add, 2)
                bot.total_value = round(bot.total_value + add, 2)
        db.add(
            models.NewsEvent(
                day=state.day,
                headline="{name} pays cash dividend",
                summary="dividend",
                category="stock",
                scope="stock",
                kind="dividend",
                stock_id=stock.id,
                impact_pct=impact,
            )
        )
    db.commit()
    return results
