"""Simulated market participants who trade real positions every day."""

import random
from collections import defaultdict

from sqlalchemy.orm import Session

from .. import models
from .orderbook import execute_market_order

MAX_TRADES_PER_BOT = 4
MIN_TRADE_NOTIONAL = 800.0
NOISE_TRADE_CHANCE = 0.4
COST_RATE = 0.002


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _target_weights(bot: models.Rival, stocks: list[models.Stock]) -> dict[int, float]:
    strategy = bot.strategy
    raw: dict[int, float] = {}
    for stock in stocks:
        momentum = stock.momentum_20d or 0.0
        if strategy == "index":
            value = 1.0
        elif strategy == "momentum":
            value = max(0.0, momentum) ** 1.5 + 0.01
        elif strategy == "value":
            value = 1.0 / max(stock.pe_ratio, 1.0)
        elif strategy == "low volatility":
            value = 1.0 / max(stock.volatility, 0.002)
        elif strategy == "growth":
            value = max(0.0, momentum) * stock.pe_ratio + 0.01
        elif strategy == "quant":
            value = max(0.0, momentum) * 0.5 + (1.0 / max(stock.pe_ratio, 1.0)) * 12.0
        elif strategy == "retail_chase":
            value = max(0.0, momentum) ** 3 + 0.001
        elif strategy == "retail_panic":
            value = 1.0
        elif strategy == "retail_allin":
            value = max(0.0, momentum) ** 4 + 0.001
        elif strategy == "retail_limit":
            limit = (stock.limit_pct or 10.0) / 100.0
            value = (
                1.0
                if (stock.prev_daily_ret or 0.0) >= limit - 0.01
                else 0.001
            )
        elif strategy == "retail_knife":
            value = max(0.0, -(stock.momentum_60d or 0.0)) ** 1.5 + 0.001
        elif strategy == "retail_follower":
            value = max(0.0, momentum) ** 2 + 0.001
        elif strategy == "retail_margin":
            value = 1.0
        elif strategy == "retail_sleeper":
            value = 1.0 / max(stock.volatility * max(stock.beta, 0.3), 0.002) + 0.01
        elif strategy == "rotation":
            value = 1.0
        else:  # dynamic and anything unknown
            value = 1.0
        raw[stock.id] = value

    if strategy == "rotation":
        sector_momentum: dict[str, float] = defaultdict(float)
        sector_count: dict[str, int] = defaultdict(int)
        for stock in stocks:
            sector_momentum[stock.industry] += stock.momentum_20d or 0.0
            sector_count[stock.industry] += 1
        scores = {
            sector: momentum / max(count, 1)
            for sector, momentum in sector_momentum.items()
            for count in [sector_count[sector]]
        }
        best = sorted(scores, key=lambda s: -scores[s])[:2]
        for stock in stocks:
            raw[stock.id] = 2.5 if stock.industry in best else 0.3

    total = sum(raw.values())
    if total <= 0:
        total = len(stocks)
        raw = {stock.id: 1.0 for stock in stocks}
    return {stock_id: value / total for stock_id, value in raw.items()}


def _invest_ratio(bot: models.Rival, state: models.GameState) -> float:
    cycle = state.market_cycle
    if bot.strategy == "retail_panic":
        return 0.95 if state.sentiment >= 1.05 else 0.1
    if bot.strategy == "retail_chase":
        return 0.95
    if bot.strategy == "retail_allin":
        return 0.98
    if bot.strategy in ("retail_limit", "retail_follower"):
        return 0.92
    if bot.strategy == "retail_knife":
        return 0.95
    if bot.strategy == "retail_margin":
        return 1.3 if cycle in ("bull", "recovery") else 0.95
    if bot.strategy == "retail_sleeper":
        return 0.85
    if bot.strategy == "dynamic":
        return {"bull": 0.95, "recovery": 0.9, "bear": 0.55, "recession": 0.35}[cycle]
    if bot.strategy in ("low volatility", "value"):
        return 0.92
    if bot.strategy == "momentum":
        return 0.9 if cycle in ("bull", "recovery") else 0.72
    return 0.9


def _cost_rate(bot: models.Rival) -> float:
    return 0.006 if bot.strategy.startswith("retail") else COST_RATE


def seed_bot_holdings(
    db: Session,
    rivals: list[models.Rival],
    stocks: list[models.Stock],
    rng: random.Random,
) -> None:
    price_by_id = {stock.id: stock.price for stock in stocks}
    stock_by_id = {stock.id: stock for stock in stocks}
    for bot in rivals:
        weights = _target_weights(bot, stocks)
        invest = bot.invested_value
        for stock_id, weight in weights.items():
            price = price_by_id[stock_id]
            shares = invest * weight / price
            db.add(
                models.BotHolding(
                    bot_id=bot.id,
                    stock_id=stock_id,
                    shares=shares,
                    avg_cost=price,
                )
            )


def tick_bots(
    db: Session,
    state: models.GameState,
    stocks: list[models.Stock],
    rng: random.Random,
) -> tuple[dict[int, float], dict[int, float]]:
    """Rebalance bot portfolios and return (net flow notional, traded shares)."""
    price_by_id = {stock.id: stock.price for stock in stocks}
    stock_by_id = {stock.id: stock for stock in stocks}
    flow: dict[int, float] = defaultdict(float)
    bot_volume: dict[int, float] = defaultdict(float)
    bots = db.query(models.Rival).all()

    for bot in bots:
        holdings = {
            row.stock_id: row
            for row in db.query(models.BotHolding)
            .filter(models.BotHolding.bot_id == bot.id)
            .all()
        }
        holdings_value = sum(
            row.shares * price_by_id[stock_id] for stock_id, row in holdings.items()
        )
        if bot.strategy == "retail_margin" and bot.cash + holdings_value < 75_000:
            for stock_id, holding in list(holdings.items()):
                stock = stock_by_id[stock_id]
                exec_price = execute_market_order(
                    db, stock, state, holding.shares, "sell"
                )
                if exec_price is not None:
                    proceeds = holding.shares * exec_price
                    bot.cash += proceeds * (1.0 - _cost_rate(bot))
                    flow[stock_id] -= proceeds
                    bot_volume[stock_id] += holding.shares
                    db.add(
                        models.BotTrade(
                            bot_id=bot.id,
                            stock_id=stock_id,
                            action="sell",
                            shares=holding.shares,
                            price=round(exec_price, 2),
                            notional=round(proceeds, 2),
                            day=state.day,
                        )
                    )
                db.delete(holding)
                db.flush()
            holdings.clear()
            holdings_value = 0.0
            bot.cash = 55_000.0
        weights = _target_weights(bot, stocks)
        target_value = (bot.cash + holdings_value) * _invest_ratio(bot, state)

        diffs = []
        for stock_id, weight in weights.items():
            price = price_by_id[stock_id]
            target_shares = target_value * weight / price
            current = holdings[stock_id].shares if stock_id in holdings else 0.0
            diff = target_shares - current
            if (
                stock_by_id[stock_id].liquidity_factor < 0.6
                and current > 0
                and bot.strategy in ("momentum", "dynamic", "quant", "growth")
            ):
                diff = -0.25 * current
            if abs(diff * price) >= MIN_TRADE_NOTIONAL:
                diffs.append((stock_id, diff, price))

        diffs.sort(key=lambda item: -abs(item[1] * item[2]))
        cash = bot.cash
        max_trades = 6 if bot.strategy.startswith("retail") else MAX_TRADES_PER_BOT
        noise_chance = 0.6 if bot.strategy.startswith("retail") else NOISE_TRADE_CHANCE
        cost_rate = _cost_rate(bot)
        executed = 0
        traded_this_bot = set()
        for stock_id, diff, price in diffs:
            if executed >= max_trades:
                break
            lot = 100 if price >= 10 else 500
            shares = int(diff / lot) * lot
            if shares == 0:
                continue
            holding = holdings.get(stock_id)
            if diff > 0:
                ask = stock_by_id[stock_id].ask or price
                max_by_cash = int((cash - 100.0) / ask / lot) * lot
                shares = min(shares, max_by_cash)
                if shares <= 0:
                    continue
                exec_price = execute_market_order(
                    db, stock_by_id[stock_id], state, shares, "buy"
                )
                if exec_price is None:
                    continue
                notional = shares * exec_price
                cash -= notional * (1.0 + cost_rate)
                if holding is None:
                    holding = models.BotHolding(
                        bot_id=bot.id,
                        stock_id=stock_id,
                        shares=0.0,
                        avg_cost=0.0,
                    )
                    db.add(holding)
                    holdings[stock_id] = holding
                new_shares = holding.shares + shares
                holding.avg_cost = (
                    holding.shares * holding.avg_cost + notional
                ) / new_shares
                holding.shares = new_shares
                action = "buy"
            else:
                available = int(holding.shares / lot) * lot if holding else 0
                shares = min(abs(shares), available)
                if shares <= 0:
                    continue
                exec_price = execute_market_order(
                    db, stock_by_id[stock_id], state, shares, "sell"
                )
                if exec_price is None:
                    continue
                notional = shares * exec_price
                cash += notional * (1.0 - cost_rate)
                holding.shares -= shares
                action = "sell"
                if holding.shares <= 1e-9:
                    db.delete(holding)
                    db.flush()
                    holdings.pop(stock_id, None)
            executed += 1
            traded_this_bot.add(stock_id)
            flow[stock_id] += notional if action == "buy" else -notional
            bot_volume[stock_id] += shares
            db.add(
                models.BotTrade(
                    bot_id=bot.id,
                    stock_id=stock_id,
                    action=action,
                    shares=shares,
                        price=round(exec_price, 2),
                    notional=round(notional, 2),
                    day=state.day,
                )
            )
        if executed < max_trades and rng.random() < noise_chance:
            candidates = [stock for stock in stocks if stock.id not in traded_this_bot]
            if candidates:
                stock = rng.choice(candidates)
                momentum_bias = (stock.momentum_20d or 0.0) * 2.0
                buy_prob = min(0.85, max(0.15, 0.5 + momentum_bias))
                action = "buy" if rng.random() < buy_prob else "sell"
                holding = next(
                    (
                        row
                        for row in db.query(models.BotHolding)
                        .filter(
                            models.BotHolding.bot_id == bot.id,
                            models.BotHolding.stock_id == stock.id,
                        )
                        .all()
                    ),
                    None,
                )
                notional = rng.uniform(2_000.0, 6_000.0)
                price = stock.price
                lot = 100 if price >= 10 else 500
                shares = int(notional / price / lot) * lot
                if action == "buy":
                    max_by_cash = int((cash - 100.0) / price / lot) * lot
                    shares = min(shares, max_by_cash)
                    if stock.ask_depth <= 0:
                        shares = 0
                else:
                    available = int((holding.shares if holding else 0) / lot) * lot
                    shares = min(shares, available)
                    if stock.bid_depth <= 0:
                        shares = 0
                if shares > 0:
                    exec_price = execute_market_order(
                        db, stock, state, shares, action
                    )
                    cost = shares * exec_price
                    if action == "buy":
                        cash -= cost * (1.0 + cost_rate)
                        if holding is None:
                            holding = models.BotHolding(
                                bot_id=bot.id,
                                stock_id=stock.id,
                                shares=0.0,
                                avg_cost=0.0,
                            )
                            db.add(holding)
                        new_shares = holding.shares + shares
                        holding.avg_cost = (
                            holding.shares * holding.avg_cost + cost
                        ) / new_shares
                        holding.shares = new_shares
                    else:
                        cash += cost * (1.0 - cost_rate)
                        holding.shares -= shares
                        if holding.shares <= 1e-9:
                            db.delete(holding)
                            db.flush()
                    flow[stock.id] += cost if action == "buy" else -cost
                    bot_volume[stock.id] += shares
                    db.add(
                        models.BotTrade(
                            bot_id=bot.id,
                            stock_id=stock.id,
                            action=action,
                            shares=shares,
                            price=round(exec_price, 2),
                            notional=round(cost, 2),
                            day=state.day,
                        )
                    )
        if bot.strategy == "retail_chase":
            gainers = [
                stock
                for stock in stocks
                if (stock.prev_daily_ret or 0.0) > 0.035
                and stock.id not in traded_this_bot
            ][:2]
            losers = [
                stock
                for stock in stocks
                if (stock.prev_daily_ret or 0.0) < -0.02
                and stock.id not in traded_this_bot
            ][:2]
            for stock in gainers:
                if executed >= max_trades:
                    break
                notional = (bot.cash + holdings_value) * 0.012
                price = stock.ask or stock.price
                lot = 100 if price >= 10 else 500
                shares = int(notional / price / lot) * lot
                if shares <= 0:
                    continue
                exec_price = execute_market_order(db, stock, state, shares, "buy")
                if exec_price is None:
                    continue
                cost = shares * exec_price
                if cash < cost * (1.0 + cost_rate):
                    continue
                cash -= cost * (1.0 + cost_rate)
                holding = holdings.get(stock.id)
                if holding is None:
                    holding = models.BotHolding(
                        bot_id=bot.id,
                        stock_id=stock.id,
                        shares=0.0,
                        avg_cost=0.0,
                    )
                    db.add(holding)
                    holdings[stock.id] = holding
                new_shares = holding.shares + shares
                holding.avg_cost = (
                    holding.shares * holding.avg_cost + cost
                ) / new_shares
                holding.shares = new_shares
                traded_this_bot.add(stock.id)
                executed += 1
                flow[stock.id] += cost
                bot_volume[stock.id] += shares
                db.add(
                    models.BotTrade(
                        bot_id=bot.id,
                        stock_id=stock.id,
                        action="buy",
                        shares=shares,
                        price=round(exec_price, 2),
                        notional=round(cost, 2),
                        day=state.day,
                    )
                )
            for stock in losers:
                if executed >= max_trades:
                    break
                holding = holdings.get(stock.id)
                if holding is None:
                    continue
                lot = 100 if stock.price >= 10 else 500
                shares = int(holding.shares * 0.25 / lot) * lot
                if shares <= 0:
                    continue
                exec_price = execute_market_order(db, stock, state, shares, "sell")
                if exec_price is None:
                    continue
                cost = shares * exec_price
                cash += cost * (1.0 - cost_rate)
                holding.shares -= shares
                if holding.shares <= 1e-9:
                    db.delete(holding)
                    db.flush()
                    holdings.pop(stock.id, None)
                traded_this_bot.add(stock.id)
                executed += 1
                flow[stock.id] -= cost
                bot_volume[stock.id] += shares
                db.add(
                    models.BotTrade(
                        bot_id=bot.id,
                        stock_id=stock.id,
                        action="sell",
                        shares=shares,
                        price=round(exec_price, 2),
                        notional=round(cost, 2),
                        day=state.day,
                    )
                )
        if bot.strategy == "retail_margin" and holdings_value > 0:
            cash -= holdings_value * 0.0008
        bot.cash = round(max(0.0, cash), 2)
    return flow, bot_volume


def refresh_rival_values(db: Session, day: int | None = None) -> None:
    """Mark every bot to market and snapshot its equity when a day is given."""
    price_by_id = {
        stock.id: stock.price
        for stock in db.query(models.Stock).all()
    }
    for bot in db.query(models.Rival).all():
        invested = sum(
            row.shares * price_by_id[row.stock_id]
            for row in db.query(models.BotHolding)
            .filter(models.BotHolding.bot_id == bot.id)
            .all()
        )
        bot.invested_value = invested
        bot.total_value = bot.cash + invested
        if day is not None:
            db.add(
                models.BotHistory(
                    bot_id=bot.id,
                    day=day,
                    value=round(bot.total_value, 2),
                    cash=round(bot.cash, 2),
                    invested=round(invested, 2),
                )
            )


def flow_impact(notional: float, avg_volume: int, price: float) -> float:
    denominator = max(1.0, avg_volume * price)
    return _clamp(notional / denominator * 2.5, -0.015, 0.015)
