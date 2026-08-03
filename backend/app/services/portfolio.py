import math

from sqlalchemy.orm import Session

from .. import models
from ..config import FEE_RATE, MIN_FEE, MIN_ORDER_NOTIONAL, STARTING_CASH
from ..i18n import company_name
from ..services.orderbook import estimate_market_order, execute_market_order


def get_or_create_player(db: Session) -> models.Player:
    player = db.query(models.Player).first()
    if player is None:
        player = models.Player(
            name="Player One",
            starting_cash=STARTING_CASH,
            cash=STARTING_CASH,
        )
        db.add(player)
        db.flush()
        db.add(
            models.PortfolioHistory(
                player_id=player.id,
                day=0,
                date=db.query(models.GameState).first().date,
                value=STARTING_CASH,
                cash=STARTING_CASH,
                invested=0.0,
            )
        )
        db.commit()
    return player


def portfolio_value(db: Session, player: models.Player) -> float:
    invested = 0.0
    for holding in db.query(models.Holding).filter(models.Holding.player_id == player.id):
        stock = db.get(models.Stock, holding.stock_id)
        invested += holding.shares * stock.price
    return player.cash + invested


def latest_snapshot(db: Session, player: models.Player) -> models.PortfolioHistory | None:
    return (
        db.query(models.PortfolioHistory)
        .filter(models.PortfolioHistory.player_id == player.id)
        .order_by(models.PortfolioHistory.day.desc())
        .first()
    )


def portfolio_summary(db: Session, player: models.Player | None = None) -> dict:
    player = player or get_or_create_player(db)
    value = round(portfolio_value(db, player), 2)
    invested = round(value - player.cash, 2)
    total_return = (value - player.starting_cash) / player.starting_cash

    snapshot = latest_snapshot(db, player)
    if snapshot:
        daily_pnl = round(value - snapshot.value, 2)
        day_change_pct = (daily_pnl / snapshot.value) if snapshot.value else 0.0
    else:
        daily_pnl = 0.0
        day_change_pct = 0.0

    return {
        "cash": round(player.cash, 2),
        "invested": invested,
        "value": value,
        "starting_cash": player.starting_cash,
        "total_return": round(total_return, 6),
        "total_return_pct": round(total_return * 100, 2),
        "daily_pnl": daily_pnl,
        "day_change_pct": round(day_change_pct * 100, 3),
        "profit": round(value - player.starting_cash, 2),
    }


def holdings_detail(db: Session, player: models.Player, lang: str = "en") -> list[dict]:
    rows = []
    holdings = (
        db.query(models.Holding)
        .filter(models.Holding.player_id == player.id)
        .order_by(models.Holding.id)
        .all()
    )
    for holding in holdings:
        stock = db.get(models.Stock, holding.stock_id)
        market_value = round(holding.shares * stock.price, 2)
        cost_basis = round(holding.shares * holding.avg_cost, 2)
        unrealized = round(market_value - cost_basis, 2)
        rows.append(
            {
                "ticker": stock.ticker,
                "name": company_name(lang, stock.ticker, stock.name),
                "industry": stock.industry,
                "shares": round(holding.shares, 4),
                "locked_shares": round(holding.locked_shares or 0.0, 4),
                "price": round(stock.price, 2),
                "avg_cost": round(holding.avg_cost, 4),
                "cost_basis": cost_basis,
                "market_value": market_value,
                "unrealized_pnl": unrealized,
                "unrealized_pct": round(unrealized / cost_basis * 100, 2) if cost_basis else 0.0,
                "day_change_pct": round((stock.price / stock.prev_close - 1.0) * 100, 3),
                "weight": 0.0,
            }
        )
    total = sum(row["market_value"] for row in rows)
    for row in rows:
        row["weight"] = round(row["market_value"] / total * 100, 2) if total else 0.0
    return rows


def allocation(db: Session, player: models.Player) -> dict:
    weights: dict[str, float] = {}
    total = 0.0
    for holding in db.query(models.Holding).filter(models.Holding.player_id == player.id):
        stock = db.get(models.Stock, holding.stock_id)
        value = holding.shares * stock.price
        weights[stock.industry] = weights.get(stock.industry, 0.0) + value
        total += value
    breakdown = [
        {
            "industry": industry,
            "value": round(value, 2),
            "weight": round(value / total * 100, 2) if total else 0.0,
        }
        for industry, value in sorted(weights.items(), key=lambda item: -item[1])
    ]
    return {"breakdown": breakdown, "total_invested": round(total, 2)}


def performance(db: Session, player: models.Player, limit: int = 260) -> dict:
    rows = (
        db.query(models.PortfolioHistory)
        .filter(models.PortfolioHistory.player_id == player.id)
        .order_by(models.PortfolioHistory.day.desc())
        .limit(limit)
        .all()
    )
    rows = list(reversed(rows))
    points = [
        {
            "day": row.day,
            "date": row.date,
            "value": row.value,
            "cash": row.cash,
            "invested": row.invested,
        }
        for row in rows
    ]
    return {"series": points}


def _affordable_buy_shares(
    player: models.Player,
    stock: models.Stock,
    state: models.GameState,
    requested: float,
) -> float:
    """Largest buy size that fits cash at the expected fill price, including fees."""
    shares = round(requested, 4)
    if shares <= 0:
        return 0.0

    def total_cost(count: float) -> float:
        price = estimate_market_order(stock, state, count, "buy")
        if price is None or price <= 0:
            return float("inf")
        gross = count * price
        return gross + max(MIN_FEE, gross * FEE_RATE)

    if total_cost(shares) <= player.cash + 1e-6:
        return shares

    low, high = 0.0, shares
    for _ in range(40):
        mid = (low + high) / 2.0
        if total_cost(mid) <= player.cash + 1e-6:
            low = mid
        else:
            high = mid
    return math.floor(low * 100) / 100


def execute_trade(
    db: Session,
    player: models.Player,
    stock: models.Stock,
    action: str,
    shares: float,
    dark_pool: bool = False,
) -> dict:
    shares = round(shares, 4)
    state = db.query(models.GameState).first()
    if action == "buy":
        shares = _affordable_buy_shares(player, stock, state, shares)
        if shares <= 0:
            raise ValueError(
                "\u73b0\u91d1\u4e0d\u8db3\uff0c\u65e0\u6cd5\u5b8c\u6210\u8be5\u8ba2\u5355\uff08\u542b\u624b\u7eed\u8d39\uff09"
            )
    if dark_pool:
        mid = (stock.bid + stock.ask) / 2.0 if stock.bid and stock.ask else stock.price
        exec_price = round(mid, 4)
        pool_shares = int(stock.avg_volume * 0.02)
        if shares > pool_shares:
            raise ValueError("Dark pool liquidity exceeded; reduce size or use the exchange")
    else:
        exec_price = execute_market_order(db, stock, state, shares, action)
    if exec_price is None:
        if action == "buy":
            raise ValueError("\u6da8\u505c\u4e2d\uff0c\u6682\u65f6\u65e0\u6cd5\u4e70\u5165")
        raise ValueError("\u8dcc\u505c\u4e2d\uff0c\u6682\u65f6\u65e0\u6cd5\u5356\u51fa")
    gross = round(shares * exec_price, 2)
    if gross < MIN_ORDER_NOTIONAL:
        raise ValueError(f"Minimum order size is ${MIN_ORDER_NOTIONAL:,.0f}.")
    fee = round(max(MIN_FEE, gross * FEE_RATE), 2)
    stamp_tax = round(gross * 0.0005, 2) if action == "sell" else 0.0

    holding = (
        db.query(models.Holding)
        .filter(
            models.Holding.player_id == player.id,
            models.Holding.stock_id == stock.id,
        )
        .first()
    )

    if action == "buy":
        total_cost = gross + fee
        if player.cash + 0.02 < total_cost:
            raise ValueError(
                "\u73b0\u91d1\u4e0d\u8db3\uff0c\u65e0\u6cd5\u5b8c\u6210\u8be5\u8ba2\u5355\uff08\u542b\u624b\u7eed\u8d39\uff09"
            )
        if holding is None:
            holding = models.Holding(
                player_id=player.id,
                stock_id=stock.id,
                shares=0.0,
                avg_cost=0.0,
            )
            db.add(holding)
            db.flush()
        new_shares = holding.shares + shares
        holding.avg_cost = (holding.shares * holding.avg_cost + gross) / new_shares
        holding.shares = new_shares
        holding.locked_shares = round((holding.locked_shares or 0.0) + shares, 4)
        player.cash = round(player.cash - total_cost, 2)
        net = -total_cost
        realized_pnl = 0.0
    else:
        if holding is None or holding.shares + 1e-9 < shares:
            raise ValueError("You do not own enough shares to sell.")
        sellable = holding.shares - (holding.locked_shares or 0.0)
        if shares > sellable + 1e-9:
            raise ValueError("\u5f53\u65e5\u4e70\u5165\u7684\u4efd\u989d\u6682\u4e0d\u53ef\u5356\u51fa\uff08T+1\uff09")
        realized_pnl = round((exec_price - holding.avg_cost) * shares - fee - stamp_tax, 2)
        holding.shares = round(holding.shares - shares, 4)
        player.cash = round(player.cash + gross - fee - stamp_tax, 2)
        net = gross - fee - stamp_tax
        if holding.shares <= 1e-9:
            db.delete(holding)

    transaction = models.Transaction(
        player_id=player.id,
        stock_id=stock.id,
        action=action,
        shares=shares,
        price=round(exec_price, 2),
        gross=gross,
        fee=fee,
        stamp_tax=stamp_tax,
        net=net,
        realized_pnl=realized_pnl,
        day=state.day,
        dark_pool=1 if dark_pool else 0,
    )
    db.add(transaction)
    if not dark_pool:
        stock.volume = int((stock.volume or 0) + shares)
        avg_volume = stock.avg_volume or 1
        flow_ratio = shares / avg_volume
        magnitude = min(0.012, max(0.0002, flow_ratio * 2.0))
        impact = magnitude if action == "buy" else -magnitude
        stock.player_impact = round((stock.player_impact or 0.0) + impact, 6)
        stock.price = round(stock.price * (1 + impact), 4)
    db.commit()
    return {
        "id": transaction.id,
        "action": action,
        "ticker": stock.ticker,
        "shares": shares,
        "price": round(exec_price, 2),
        "gross": gross,
        "fee": fee,
        "stamp_tax": stamp_tax,
        "net": net,
        "realized_pnl": realized_pnl,
        "day": state.day,
        "dark_pool": dark_pool,
        "cash": player.cash,
    }


def transaction_history(
    db: Session, player: models.Player, limit: int = 100, lang: str = "en"
) -> list[dict]:
    rows = (
        db.query(models.Transaction)
        .filter(models.Transaction.player_id == player.id)
        .order_by(models.Transaction.id.desc())
        .limit(limit)
        .all()
    )
    result = []
    for row in rows:
        stock = db.get(models.Stock, row.stock_id)
        result.append(
            {
                "id": row.id,
                "action": row.action,
                "ticker": stock.ticker,
                "name": company_name(lang, stock.ticker, stock.name),
                "shares": row.shares,
                "price": row.price,
                "gross": row.gross,
                "fee": row.fee,
                "stamp_tax": row.stamp_tax,
                "net": row.net,
                "realized_pnl": row.realized_pnl,
                "day": row.day,
                "executed_at": row.executed_at,
            }
        )
    return result
