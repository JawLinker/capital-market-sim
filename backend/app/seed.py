import json
import os
import random
from datetime import date, timedelta

from sqlalchemy.orm import Session

from . import models
from .config import HISTORY_DAYS, SEED, SNAPSHOT_PATH, STARTING_CASH
from .services.fundamentals import (
    INDUSTRY_BASE_PE,
    assign_company_profile,
    fundamental_price,
)
from .services.bots import seed_bot_holdings
from .services.market_engine import next_trading_date
from .services.auth import generate_api_key, hash_password

ACHIEVEMENTS = [
    ("first_trade", "First Trade", "Execute your first buy order.", "trading"),
    ("first_sell", "Round Trip", "Complete your first sell order.", "trading"),
    ("trade_10", "Active Trader", "Execute 10 trades.", "trading"),
    ("trade_50", "Liquidity Provider", "Execute 50 trades.", "trading"),
    ("trade_100", "Market Veteran", "Execute 100 trades.", "trading"),
    ("five_sectors", "Diversified", "Hold positions in all five industries.", "strategy"),
    ("concentrated", "All In", "Let a single stock reach more than 60% of your portfolio.", "risk"),
    ("cash_king", "Cash Commander", "Hold more than 70% of your portfolio in cash after day 20.", "strategy"),
    ("value_finder", "Value Finder", "Own a stock the advisor rates as undervalued.", "strategy"),
    ("momentum_rider", "Momentum Rider", "Own a stock with 20-day momentum above 10%.", "strategy"),
    ("bear_survivor", "Bear Survivor", "Complete a full trading week while the market is in a bear cycle.", "risk"),
    ("green_day", "Green Day", "Gain more than 1.5% of portfolio value in a single day.", "trading"),
    ("red_day", "Risk Tolerance", "Lose more than 2% of portfolio value in a single day.", "risk"),
    ("milestone_110k", "First Milestone", "Reach a portfolio value of ¥110,000.", "milestone"),
    ("milestone_150k", "Strong Hands", "Reach a portfolio value of ¥150,000.", "milestone"),
    ("milestone_200k", "Six-Figure Club", "Reach a portfolio value of ¥200,000.", "milestone"),
    ("day_30", "One Month In", "Complete 30 trading days.", "milestone"),
    ("day_100", "Seasoned Investor", "Complete 100 trading days.", "milestone"),
]

RIVALS = [
    ("Aurora Capital", "index", 0.03, 1.06, {"technology": 0.2, "healthcare": 0.2, "energy": 0.2, "finance": 0.2, "consumer": 0.2}),
    ("Hawk Momentum Fund", "momentum", 0.08, 1.12, {"technology": 0.35, "healthcare": 0.25, "energy": 0.15, "finance": 0.1, "consumer": 0.15}),
    ("Granite Value Partners", "value", 0.05, 1.03, {"technology": 0.1, "healthcare": 0.2, "energy": 0.25, "finance": 0.3, "consumer": 0.15}),
    ("Sector Rotation Group", "rotation", 0.04, 1.1, {"technology": 0.3, "healthcare": 0.3, "energy": 0.1, "finance": 0.2, "consumer": 0.1}),
    ("Turtle Income Trust", "low volatility", 0.12, 0.99, {"technology": 0.05, "healthcare": 0.15, "energy": 0.25, "finance": 0.35, "consumer": 0.2}),
    ("Nimbus Growth Fund", "growth", 0.06, 1.15, {"technology": 0.4, "healthcare": 0.3, "energy": 0.1, "finance": 0.05, "consumer": 0.15}),
    ("Palisade Hedge Fund", "dynamic", 0.1, 1.08, {"technology": 0.25, "healthcare": 0.2, "energy": 0.2, "finance": 0.2, "consumer": 0.15}),
    ("Cipher Quant Lab", "quant", 0.02, 1.13, {"technology": 0.3, "healthcare": 0.2, "energy": 0.15, "finance": 0.25, "consumer": 0.1}),
    ("Chase Retail Fund", "retail_chase", 0.05, 0.97, {"technology": 0.3, "healthcare": 0.2, "energy": 0.2, "finance": 0.15, "consumer": 0.15}),
    ("Panic Retail Fund", "retail_panic", 0.5, 0.96, {"technology": 0.2, "healthcare": 0.2, "energy": 0.2, "finance": 0.2, "consumer": 0.2}),
    ("All-In Retail Fund", "retail_allin", 0.05, 0.95, {"technology": 0.3, "healthcare": 0.2, "energy": 0.2, "finance": 0.15, "consumer": 0.15}),
    ("Limit-Up Chaser Fund", "retail_limit", 0.08, 0.94, {"technology": 0.3, "healthcare": 0.2, "energy": 0.2, "finance": 0.15, "consumer": 0.15}),
    ("Knife Catcher Fund", "retail_knife", 0.06, 0.93, {"technology": 0.2, "healthcare": 0.2, "energy": 0.2, "finance": 0.2, "consumer": 0.2}),
    ("Follower Retail Fund", "retail_follower", 0.05, 0.92, {"technology": 0.3, "healthcare": 0.2, "energy": 0.2, "finance": 0.15, "consumer": 0.15}),
    ("Margin Retail Fund", "retail_margin", 0.05, 1.1, {"technology": 0.3, "healthcare": 0.2, "energy": 0.2, "finance": 0.15, "consumer": 0.15}),
    ("Sleeper Retail Fund", "retail_sleeper", 0.08, 0.95, {"technology": 0.15, "healthcare": 0.25, "energy": 0.2, "finance": 0.25, "consumer": 0.15}),
]

_RETAIL_STYLES = [
    "retail_chase",
    "retail_panic",
    "retail_allin",
    "retail_limit",
    "retail_knife",
    "retail_follower",
    "retail_margin",
]
for _index in range(20):
    _style = _RETAIL_STYLES[_index % len(_RETAIL_STYLES)]
    RIVALS.append(
        (
            f"Retail Trader {_index + 1:02d}",
            _style,
            0.5 if _style == "retail_panic" else 0.05,
            round(0.85 + (_index % 8) * 0.015, 3),
            {"technology": 0.25, "healthcare": 0.2, "energy": 0.2, "finance": 0.15, "consumer": 0.2},
        )
    )


def trading_dates(count: int) -> list[str]:
    result = []
    current = date(2019, 1, 2)
    while len(result) < count:
        if current.weekday() < 5:
            result.append(current.isoformat())
        current += timedelta(days=1)
    return result


def _load_snapshot() -> dict:
    with SNAPSHOT_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def seed_database(db: Session) -> bool:
    if db.query(models.Stock).first() is not None:
        return False

    rng = random.Random(SEED)
    snapshot = _load_snapshot()
    longest = max(snapshot["stocks"], key=lambda entry: len(entry["series"]))
    dates = [point["d"] for point in longest["series"][:HISTORY_DAYS]]
    index_rows = snapshot["meta"].get("index_series") or []
    shanghai_index = round(index_rows[HISTORY_DAYS - 1]["c"], 2) if len(index_rows) > HISTORY_DAYS else 3000.0
    shanghai_prev = round(index_rows[HISTORY_DAYS - 2]["c"], 2) if len(index_rows) > HISTORY_DAYS - 1 else shanghai_index

    stocks = []
    for entry in snapshot["stocks"]:
        series = entry["series"][:HISTORY_DAYS]
        entry["_slice"] = series
        closes = [point["c"] for point in series]
        stock = models.Stock(
            ticker=entry["ticker"],
            name=entry["real_name"],
            industry=entry["industry"],
            price=round(series[-1]["c"], 2),
            prev_close=round(series[-2]["c"], 2),
            volatility=entry["volatility"],
            market_cap=entry["market_cap"],
            pe_ratio=entry["pe_ratio"],
            beta=entry["beta"],
            fundamental_price=round(series[-1]["c"], 2),
            volume=int(series[-1]["v"]),
            avg_volume=entry["avg_volume"],
            fifty_two_week_high=round(max(closes), 2),
            fifty_two_week_low=round(min(closes), 2),
            momentum_20d=round(closes[-1] / closes[-21] - 1.0, 6),
            momentum_60d=round(closes[-1] / closes[-61] - 1.0, 6),
            prev_daily_ret=round(closes[-1] / closes[-2] - 1.0, 6),
        )
        db.add(stock)
        stocks.append(stock)
    db.flush()
    for stock, entry in zip(stocks, snapshot["stocks"]):
        assign_company_profile(stock, rng)
        stock.pe_ratio = entry["pe_ratio"]
        stock.eps_estimate = round(max(0.05, stock.price / (entry["pe_ratio"] * 4.0)), 4)
        stock.eps_actual = stock.eps_estimate
        stock.fundamental_price = fundamental_price(stock, 4.25, 1.0)
        stock.bid = round(stock.price * 0.999, 2)
        stock.ask = round(stock.price * 1.001, 2)
        stock.bid_depth = int(max(200, stock.avg_volume * 0.004))
        stock.ask_depth = int(max(200, stock.avg_volume * 0.004))
        stock.liquidity_factor = 1.0
        stock.limit_pct = (
            20.0
            if entry["real_code"].startswith(("300", "301", "688", "689"))
            else 10.0
        )

    rows = []
    for stock, entry in zip(stocks, snapshot["stocks"]):
        series = entry["_slice"]
        for index, point in enumerate(series):
            rows.append(
                models.PriceHistory(
                    stock_id=stock.id,
                    trade_date=point["d"],
                    open=point["o"],
                    high=point["h"],
                    low=point["l"],
                    close=point["c"],
                    volume=int(point["v"]),
                )
            )
    db.add_all(rows)

    player = models.Player(
        name="Host",
        username="host",
        password_hash=hash_password(os.environ.get("CMS_HOST_PASSWORD", "123456")),
        api_key=generate_api_key(),
        is_host=1,
        starting_cash=STARTING_CASH,
        cash=STARTING_CASH,
    )
    db.add(player)
    db.flush()

    state = models.GameState(
        id=1,
        day=0,
        date=dates[-1],
        market_cycle="recovery",
        sentiment=1.0,
        regime_strength=1.0,
        benchmark_value=100.0,
        benchmark_prev=100.0,
        next_regime_day=rng.randint(8, 16),
        policy_rate=4.25,
        inflation=3.1,
        style_factor=0.0,
        next_rate_day=rng.randint(10, 20),
        regime_count=2,
        replay_index=HISTORY_DAYS,
        shanghai_index=shanghai_index,
        shanghai_prev=shanghai_prev,
    )
    db.add(state)

    db.add(
        models.PortfolioHistory(
            player_id=player.id,
            day=0,
            date=dates[-1],
            value=STARTING_CASH,
            cash=STARTING_CASH,
            invested=0.0,
        )
    )

    for code, title, description, category in ACHIEVEMENTS:
        db.add(
            models.Achievement(
                code=code,
                title=title,
                description=description,
                category=category,
            )
        )

    rivals = []
    for name, strategy, cash_pct, factor, weights in RIVALS:
        total = STARTING_CASH * factor
        cash = total * cash_pct
        rival = models.Rival(
            name=name,
            strategy=strategy,
            cash=cash,
            invested_value=total - cash,
            total_value=total,
            weights=json.dumps(weights),
        )
        db.add(rival)
        rivals.append(rival)
    db.flush()
    seed_bot_holdings(db, rivals, stocks, rng)
    for rival in rivals:
        db.add(
            models.BotHistory(
                bot_id=rival.id,
                day=0,
                value=round(rival.total_value, 2),
                cash=round(rival.cash, 2),
                invested=round(rival.invested_value, 2),
            )
        )

    db.commit()
    return True
