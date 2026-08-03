"""Deterministic intraday price path for live trading within a day window."""

import random


def intraday_price(stock, day: int, elapsed: float, window: float) -> float:
    if window <= 0:
        return round(stock.price, 4)
    frac = max(0.0, min(1.0, elapsed / window))
    rng = random.Random(stock.id * 7919 + day)
    points = [rng.uniform(-0.012, 0.012) for _ in range(5)]
    pos = frac * 4
    index = min(4, int(pos))
    t = pos - index
    path = points[index] * (1 - t) + points[min(4, index + 1)] * t
    base = stock.price
    band = (stock.limit_pct or 10.0) / 100.0
    return round(
        max(base * (1 - band), min(base * (1 + band), base * (1 + path))),
        4,
    )
