"""Fundamental valuation and macro drivers for the market engine."""

import math
import random

BASE_RATE = 4.0

INDUSTRY_BASE_PE = {
    "technology": 38.0,
    "healthcare": 32.0,
    "energy": 18.0,
    "finance": 14.0,
    "consumer": 24.0,
}

INDUSTRY_ORDER = ["technology", "healthcare", "energy", "finance", "consumer"]

# Correlation matrix for daily industry shocks. Tech, finance, and consumer are
# more market-like; healthcare is defensive; energy is more idiosyncratic.
INDUSTRY_CORRELATION = [
    [1.0, 0.45, 0.25, 0.55, 0.50],
    [0.45, 1.0, 0.20, 0.35, 0.40],
    [0.25, 0.20, 1.0, 0.40, 0.25],
    [0.55, 0.35, 0.40, 1.0, 0.45],
    [0.50, 0.40, 0.25, 0.45, 1.0],
]

GROWTH_RANGE_BY_INDUSTRY = {
    "technology": (0.12, 0.30),
    "healthcare": (0.10, 0.26),
    "energy": (0.03, 0.12),
    "finance": (0.04, 0.14),
    "consumer": (0.04, 0.16),
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _cholesky(matrix: list[list[float]]) -> list[list[float]]:
    size = len(matrix)
    lower = [[0.0] * size for _ in range(size)]
    for row in range(size):
        for col in range(row + 1):
            total = matrix[row][col] - sum(
                lower[row][k] * lower[col][k] for k in range(col)
            )
            if row == col:
                lower[row][col] = math.sqrt(max(total, 1e-9))
            else:
                lower[row][col] = total / lower[col][col]
    return lower


INDUSTRY_CHOLESKY = _cholesky(INDUSTRY_CORRELATION)


def correlated_industry_shocks(
    rng: random.Random, scale: float = 0.005
) -> dict[str, float]:
    """Draw correlated normal shocks for the five industries."""
    z = [rng.gauss(0.0, 1.0) for _ in range(len(INDUSTRY_ORDER))]
    shocks = {}
    for row, industry in enumerate(INDUSTRY_ORDER):
        value = sum(INDUSTRY_CHOLESKY[row][col] * z[col] for col in range(row + 1))
        shocks[industry] = value * scale
    return shocks


def rate_multiple_factor(policy_rate: float) -> float:
    """Lower rates expand multiples; higher rates compress them."""
    return (BASE_RATE / max(1.0, policy_rate)) ** 0.5


def sentiment_multiple_factor(sentiment: float) -> float:
    return clamp(0.7 + 0.35 * sentiment, 0.85, 1.25)


def industry_multiple(industry: str, policy_rate: float, sentiment: float) -> float:
    base = INDUSTRY_BASE_PE.get(industry, 20.0)
    return (
        base
        * rate_multiple_factor(policy_rate)
        * sentiment_multiple_factor(sentiment)
    )


def annual_eps(stock) -> float:
    return max(0.01, (stock.eps_estimate or 0.1) * 4.0)


def fundamental_price(stock, policy_rate: float, sentiment: float) -> float:
    return annual_eps(stock) * industry_multiple(stock.industry, policy_rate, sentiment)


def policy_target_rate(inflation: float, cycle: str) -> float:
    base = 2.2 + inflation * 0.45
    adjustment = {
        "bull": 0.5,
        "recovery": -0.25,
        "bear": -0.75,
        "recession": -1.5,
    }
    return clamp(base + adjustment.get(cycle, 0.0), 0.5, 10.0)


def assign_company_profile(stock, rng: random.Random) -> None:
    """Initialize earnings, growth, and style loadings after history seeding."""
    growth_lo, growth_hi = GROWTH_RANGE_BY_INDUSTRY.get(stock.industry, (0.05, 0.15))
    stock.earnings_growth = round(rng.uniform(growth_lo, growth_hi), 4)
    stock.earnings_quality = round(rng.uniform(0.45, 0.95), 3)
    stock.style_growth = round(
        clamp(
            0.15
            + stock.beta * 0.25
            + (stock.pe_ratio - 15.0) / 60.0 * 0.5
            + rng.uniform(-0.15, 0.15),
            0.05,
            0.95,
        ),
        3,
    )
    base_pe = INDUSTRY_BASE_PE.get(stock.industry, 20.0)
    stock.eps_estimate = round(max(0.05, stock.price / (base_pe * 4.0)), 4)
    stock.eps_actual = stock.eps_estimate
    stock.last_surprise_pct = 0.0
    stock.next_earnings_day = 20 + (stock.id % 63)
    stock.pe_ratio = round(stock.price / annual_eps(stock), 2)
