"""Order-book microstructure: bid/ask, depth, slippage, and liquidity shocks."""

from .. import models


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def liquidity_multiplier(state: models.GameState) -> float:
    cycle_adjust = {
        "bull": 0.15,
        "recovery": 0.1,
        "bear": -0.1,
        "recession": -0.25,
    }
    return _clamp(
        0.35 + state.sentiment * 0.45 + cycle_adjust.get(state.market_cycle, 0.0),
        0.2,
        1.4,
    )


def spread_pct(stock: models.Stock, state: models.GameState) -> float:
    base = max(0.0006, stock.volatility * 0.05)
    thinness = 1.6 - liquidity_multiplier(state)
    return _clamp(base * (0.5 + thinness), 0.0006, 0.02)


def is_limit_up(stock: models.Stock) -> bool:
    limit = (stock.limit_pct or 10.0) / 100.0
    ceiling = (stock.prev_close or stock.price) * (1.0 + limit)
    return stock.price >= ceiling - 1e-9


def is_limit_down(stock: models.Stock) -> bool:
    limit = (stock.limit_pct or 10.0) / 100.0
    floor = (stock.prev_close or stock.price) * (1.0 - limit)
    return stock.price <= floor + 1e-9


def refresh_book(stock: models.Stock, state: models.GameState) -> None:
    """Rebuild the top of book around the current price."""
    mid = stock.price
    spread = spread_pct(stock, state)
    half = spread / 2.0
    stock.bid = round(mid * (1.0 - half), 2)
    stock.ask = round(mid * (1.0 + half), 2)
    depth = int(
        max(
            200,
            stock.avg_volume * 0.004 * liquidity_multiplier(state) * stock.liquidity_factor,
        )
    )
    stock.bid_depth = depth
    stock.ask_depth = depth
    if is_limit_up(stock):
        stock.ask = stock.price
        stock.ask_depth = 0
    if is_limit_down(stock):
        stock.bid = stock.price
        stock.bid_depth = 0
    stock.liquidity_factor = min(1.0, stock.liquidity_factor + 0.12)


def estimate_market_order(
    stock: models.Stock,
    state: models.GameState,
    shares: float,
    side: str,
) -> float | None:
    """Expected fill price for a market order without mutating the book."""
    direction = 1 if side == "buy" else -1
    fill = stock.ask if side == "buy" else stock.bid
    depth = stock.ask_depth if side == "buy" else stock.bid_depth
    if side == "buy" and stock.ask_depth <= 0:
        return None
    if side == "sell" and stock.bid_depth <= 0:
        return None

    if shares <= depth:
        return round(fill, 2)

    excess = shares - depth
    impact_bps = min(0.06, (excess / max(depth, 1.0)) * 0.012)
    walk_price = fill * (1.0 + direction * impact_bps)
    exec_price = (fill * depth + walk_price * excess) / shares
    return round(exec_price, 2)


def execute_market_order(
    db,
    stock: models.Stock,
    state: models.GameState,
    shares: float,
    side: str,
) -> float | None:
    """Execute a market order against the book and return the fill price."""
    estimated = estimate_market_order(stock, state, shares, side)
    if estimated is None:
        return None
    direction = 1 if side == "buy" else -1
    fill = stock.ask if side == "buy" else stock.bid
    depth = stock.ask_depth if side == "buy" else stock.bid_depth

    if shares <= depth:
        remaining = int(depth - shares)
        if side == "buy":
            stock.ask_depth = max(0, remaining)
        else:
            stock.bid_depth = max(0, remaining)
        return estimated

    excess = shares - depth
    impact_bps = min(0.06, (excess / max(depth, 1.0)) * 0.012)
    walk_price = fill * (1.0 + direction * impact_bps)
    stock.price = round(walk_price, 2)

    spread = spread_pct(stock, state)
    half = spread / 2.0
    stock.bid = round(stock.price * (1.0 - half), 2)
    stock.ask = round(stock.price * (1.0 + half), 2)
    stock.bid_depth = int(max(200, depth * 0.15))
    stock.ask_depth = int(max(200, depth * 0.15))

    impact_pct = abs(walk_price / fill - 1.0)
    if impact_pct > 0.015 and state.sentiment < 1.0:
        stock.liquidity_factor = max(0.25, stock.liquidity_factor * 0.55)
    return estimated
