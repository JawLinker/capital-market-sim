import math
import random
from collections import defaultdict

from sqlalchemy.orm import Session

from .. import models
from ..config import SEED
from .fundamentals import (
    annual_eps,
    correlated_industry_shocks,
    fundamental_price,
    policy_target_rate,
)
from .bots import flow_impact, refresh_rival_values, tick_bots
from .orderbook import refresh_book
from .replay import index_row, next_replay_index, replay_rows

INDUSTRIES = ["technology", "healthcare", "energy", "finance", "consumer"]

MARKET_SIGMA = 0.0105
SECTOR_SIGMA = 0.006
IDIO_MULT = 0.75
AR_COEF = 0.02
REVERSION_K = 0.05
MAX_DAILY_RET = 0.18

REGIMES = {
    "bull": {
        "label": "Bull Market",
        "drift": 0.0002,
        "sentiment_base": 1.06,
        "vol_mult": 0.9,
    },
    "recovery": {
        "label": "Recovery",
        "drift": 0.00025,
        "sentiment_base": 1.12,
        "vol_mult": 1.0,
    },
    "bear": {
        "label": "Bear Market",
        "drift": -0.0012,
        "sentiment_base": 0.9,
        "vol_mult": 1.15,
    },
    "recession": {
        "label": "Recession",
        "drift": -0.002,
        "sentiment_base": 0.78,
        "vol_mult": 1.35,
    },
}

REGIME_TRANSITIONS = {
    "bull": {"bull": 0.62, "recovery": 0.13, "bear": 0.25},
    "recovery": {"bull": 0.35, "recovery": 0.4, "bear": 0.25},
    "bear": {"bear": 0.5, "recovery": 0.25, "recession": 0.25},
    "recession": {"recovery": 0.5, "recession": 0.35, "bear": 0.15},
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def normal(rng: random.Random) -> float:
    return clamp(rng.gauss(0.0, 1.0), -3.2, 3.2)


def daily_volume(avg_volume: int, r: float, rng: random.Random) -> int:
    """Mean-reverting volume around the average, spiking on large moves."""
    log_mult = (
        0.9 * (abs(r) / 0.02 - 1.0)
        + 0.35 * normal(rng)
        - 0.06125
    )
    return int(max(500, avg_volume * math.exp(clamp(log_mult, -1.8, 2.2))))


def pick_regime(rng: random.Random, current: str) -> str:
    table = REGIME_TRANSITIONS[current]
    options = list(table.keys())
    weights = [table[k] for k in options]
    return rng.choices(options, weights=weights)[0]


def next_trading_date(date_str: str) -> str:
    from datetime import date, timedelta

    current = date.fromisoformat(date_str)
    step = timedelta(days=1)
    while True:
        current += step
        if current.weekday() < 5:
            return current.isoformat()


def _event_pool():
    """(category, scope, min_impact, max_impact, headline kind)."""
    return [
        ("positive", "stock", 0.012, 0.035, "product_launch"),
        ("negative", "stock", 0.015, 0.045, "lawsuit"),
        ("negative", "stock", 0.012, 0.03, "regulation_probe"),
        ("positive", "stock", 0.01, 0.03, "analyst_upgrade"),
        ("negative", "stock", 0.01, 0.03, "analyst_downgrade"),
        ("positive", "stock", 0.01, 0.03, "guidance_raise"),
        ("negative", "stock", 0.01, 0.03, "guidance_cut"),
        ("positive", "stock", 0.025, 0.06, "fda_approval"),
        ("positive", "industry", 0.006, 0.016, "tax_credit"),
        ("negative", "industry", 0.006, 0.016, "supply_chain"),
        ("positive", "industry", 0.005, 0.014, "demand_surge"),
        ("negative", "industry", 0.005, 0.014, "labor_strike"),
        ("positive", "market", 0.002, 0.006, "policy_easing"),
        ("negative", "market", 0.002, 0.006, "inflation_surprise"),
        ("negative", "market", 0.002, 0.006, "geopolitical_risk"),
        ("positive", "market", 0.002, 0.005, "consumer_confidence"),
        ("neutral", "market", 0.002, 0.005, "volume_spike"),
    ]


EVENT_HEADLINES = {
    "earnings_beat": "{name} crushes quarterly earnings estimates, shares jump",
    "earnings_miss": "{name} misses quarterly earnings expectations",
    "dividend": "{name} pays cash dividend",
    "counterplay": "{name} faces quiet distribution",
    "product_launch": "{name} unveils next-generation flagship product",
    "lawsuit": "{name} hit with class-action lawsuit",
    "regulation_probe": "Regulators open investigation into {name}",
    "analyst_upgrade": "Analysts upgrade {name} on stronger growth outlook",
    "analyst_downgrade": "Analysts downgrade {name} citing margin pressure",
    "guidance_raise": "{name} raises full-year guidance",
    "guidance_cut": "{name} cuts full-year guidance",
    "fda_approval": "FDA approves {name}'s lead drug candidate",
    "tax_credit": "New tax credit proposal lifts {industry} sector",
    "supply_chain": "Supply chain bottlenecks pressure {industry} companies",
    "demand_surge": "Demand surge boosts {industry} outlook",
    "labor_strike": "Labor dispute threatens {industry} production",
    "policy_easing": "Central bank signals easier policy, markets rally",
    "inflation_surprise": "Hot inflation print rattles global markets",
    "geopolitical_risk": "Geopolitical tensions trigger broad risk-off move",
    "consumer_confidence": "Consumer confidence rebounds, broad rally ensues",
    "volume_spike": "Trading volumes spike as volatility normalizes",
    "rate_hike": "Central bank raises policy rate, markets pull back",
    "rate_cut": "Central bank cuts policy rate, markets rally",
    "replay_gain": "{name} rose {pct:.1f}% in the real-market replay",
    "replay_loss": "{name} fell {pct:.1f}% in the real-market replay",
}

EVENT_SUMMARIES = {
    "earnings_beat": "Revenue and profit both came in ahead of consensus, a classic earnings surprise that can re-rate a stock quickly.",
    "earnings_miss": "The company reported below expectations, which often triggers an immediate repricing of growth assumptions.",
    "dividend": "Shareholders receive a cash dividend; the price adjusts down by the payout on the ex-date.",
    "counterplay": "Some seats are quietly trimming the name, leaning against crowded retail positioning.",
    "product_launch": "A flagship launch can expand the addressable market and lift forward revenue estimates.",
    "lawsuit": "Legal exposure introduces potential settlement costs and reputational overhang.",
    "regulation_probe": "Regulatory scrutiny raises uncertainty about future business practices and fines.",
    "analyst_upgrade": "Sell-side upgrades can shift marginal demand and improve sentiment without changing fundamentals.",
    "analyst_downgrade": "Downgrades pressure sentiment even when the underlying business is unchanged.",
    "guidance_raise": "Management signaling higher future earnings often leads analysts to revise estimates up.",
    "guidance_cut": "Reduced guidance is an early warning of weakening demand or margin compression.",
    "fda_approval": "Regulatory approval unlocks a new revenue stream and removes a major binary risk.",
    "tax_credit": "Policy support can improve after-tax margins across an entire industry.",
    "supply_chain": "Input shortages and shipping delays compress margins and constrain output.",
    "demand_surge": "Rising end-market demand supports pricing power and volume growth.",
    "labor_strike": "Work stoppages reduce output and can push wages and costs higher.",
    "policy_easing": "Lower rates reduce discount rates on future cash flows and encourage risk-taking.",
    "inflation_surprise": "Unexpected inflation forces markets to price in tighter monetary policy.",
    "geopolitical_risk": "Uncertainty about global stability raises risk premiums across asset classes.",
    "consumer_confidence": "Improving consumer sentiment supports discretionary spending and corporate earnings.",
    "volume_spike": "Elevated volume often marks a shift in the balance between buyers and sellers.",
    "rate_hike": "Higher rates raise the discount rate on future earnings, which typically compresses valuations.",
    "rate_cut": "Lower rates reduce discount rates and support higher valuation multiples.",
    "replay_gain": "This move comes directly from historical A-share data, not from simulation.",
    "replay_loss": "This move comes directly from historical A-share data, not from simulation.",
}

EVENT_HEADLINES_ZH = {
    "earnings_beat": "{name}\u5b63\u5ea6\u8d22\u62a5\u5927\u8d85\u9884\u671f\uff0c\u80a1\u4ef7\u5927\u6da8",
    "earnings_miss": "{name}\u5b63\u5ea6\u8d22\u62a5\u4e0d\u53ca\u9884\u671f",
    "dividend": "{name}\u6d3e\u53d1\u73b0\u91d1\u5206\u7ea2",
    "counterplay": "{name}\u906d\u9047\u6c89\u9ed8\u51cf\u6301",
    "product_launch": "{name}\u53d1\u5e03\u65b0\u4e00\u4ee3\u65d7\u8230\u4ea7\u54c1",
    "lawsuit": "{name}\u906d\u9047\u96c6\u4f53\u8bc9\u8bbc",
    "regulation_probe": "\u76d1\u7ba1\u673a\u6784\u5bf9{name}\u5c55\u5f00\u8c03\u67e5",
    "analyst_upgrade": "\u5206\u6790\u5e08\u4e0a\u8c03{name}\u8bc4\u7ea7\uff0c\u770b\u597d\u589e\u957f\u524d\u666f",
    "analyst_downgrade": "\u5206\u6790\u5e08\u4e0b\u8c03{name}\u8bc4\u7ea7\uff0c\u62c5\u5fe7\u5229\u6da6\u7387\u627f\u538b",
    "guidance_raise": "{name}\u4e0a\u8c03\u5168\u5e74\u4e1a\u7ee9\u6307\u5f15",
    "guidance_cut": "{name}\u4e0b\u8c03\u5168\u5e74\u4e1a\u7ee9\u6307\u5f15",
    "fda_approval": "FDA\u6279\u51c6{name}\u6838\u5fc3\u5019\u9009\u836f\u7269",
    "tax_credit": "\u65b0\u7a0e\u6536\u62b5\u514d\u63d0\u6848\u63d0\u632f{industry}\u677f\u5757",
    "supply_chain": "\u4f9b\u5e94\u94fe\u74f6\u9888\u4ee4{industry}\u4f01\u4e1a\u627f\u538b",
    "demand_surge": "\u9700\u6c42\u6fc0\u589e\u6539\u5584{industry}\u524d\u666f",
    "labor_strike": "\u52b3\u8d44\u7ea0\u7eb7\u5a01\u80c1{industry}\u4ea7\u80fd",
    "policy_easing": "\u592e\u884c\u91ca\u653e\u5bbd\u677e\u4fe1\u53f7\uff0c\u5e02\u573a\u666e\u6da8",
    "inflation_surprise": "\u901a\u80c0\u6570\u636e\u8d85\u9884\u671f\uff0c\u5168\u7403\u5e02\u573a\u9707\u8361",
    "geopolitical_risk": "\u5730\u7f18\u653f\u6cbb\u7d27\u5f20\u5f15\u53d1\u5168\u9762\u907f\u9669",
    "consumer_confidence": "\u6d88\u8d39\u8005\u4fe1\u5fc3\u56de\u5347\uff0c\u5927\u76d8\u8d70\u5f3a",
    "volume_spike": "\u6ce2\u52a8\u56de\u5f52\u5e38\u6001\uff0c\u6210\u4ea4\u91cf\u653e\u5927",
    "rate_hike": "\u592e\u884c\u52a0\u606f\uff0c\u5e02\u573a\u627f\u538b\u56de\u843d",
    "rate_cut": "\u592e\u884c\u964d\u606f\uff0c\u5e02\u573a\u666e\u904d\u8d70\u5f3a",
    "replay_gain": "{name} \u4eca\u65e5\u4e0a\u6da8 {pct:.1f}%\uff08\u771f\u5b9e\u884c\u60c5\u56de\u653e\uff09",
    "replay_loss": "{name} \u4eca\u65e5\u4e0b\u8dcc {pct:.1f}%\uff08\u771f\u5b9e\u884c\u60c5\u56de\u653e\uff09",
}

EVENT_SUMMARIES_ZH = {
    "earnings_beat": "\u8425\u6536\u4e0e\u5229\u6da6\u53cc\u53cc\u8d85\u51fa\u9884\u671f\uff0c\u8fd9\u662f\u5178\u578b\u7684\u76c8\u5229\u60ca\u559c\uff0c\u53ef\u80fd\u8fc5\u901f\u63a8\u52a8\u80a1\u4ef7\u91cd\u4f30\u3002",
    "earnings_miss": "\u516c\u53f8\u4e1a\u7ee9\u4f4e\u4e8e\u9884\u671f\uff0c\u901a\u5e38\u4f1a\u5f15\u53d1\u5e02\u573a\u5bf9\u589e\u957f\u5047\u8bbe\u7684\u5feb\u901f\u4fee\u6b63\u3002",
    "dividend": "\u80a1\u4e1c\u83b7\u5f97\u73b0\u91d1\u5206\u7ea2\uff0c\u9664\u606f\u65e5\u80a1\u4ef7\u6309\u6d3e\u606f\u989d\u76f8\u5e94\u4e0b\u8c03\u3002",
    "counterplay": "\u67d0\u4e9b\u5e2d\u4f4d\u6b63\u5728\u9759\u9ed8\u51cf\u6301\uff0c\u504f\u62b5\u62e5\u6324\u7684\u6563\u6237\u4ed3\u4f4d\u3002",
    "product_launch": "\u65d7\u8230\u4ea7\u54c1\u53d1\u5e03\u6709\u671b\u6269\u5927\u53ef\u89e6\u8fbe\u5e02\u573a\uff0c\u5e76\u63d0\u632f\u672a\u6765\u8425\u6536\u9884\u671f\u3002",
    "lawsuit": "\u6cd5\u5f8b\u98ce\u9669\u5e26\u6765\u6f5c\u5728\u7684\u8d54\u507f\u6210\u672c\u4e0e\u58f0\u8a89\u538b\u529b\u3002",
    "regulation_probe": "\u76d1\u7ba1\u5ba1\u67e5\u589e\u52a0\u4e86\u672a\u6765\u7ecf\u8425\u65b9\u5f0f\u4e0e\u7f5a\u6b3e\u7684\u4e0d\u786e\u5b9a\u6027\u3002",
    "analyst_upgrade": "\u5356\u65b9\u4e0a\u8c03\u8bc4\u7ea7\u53ef\u5728\u57fa\u672c\u9762\u4e0d\u53d8\u7684\u60c5\u51b5\u4e0b\u6539\u5584\u5e02\u573a\u60c5\u7eea\u3002",
    "analyst_downgrade": "\u5373\u4f7f\u4e1a\u52a1\u672c\u8eab\u6ca1\u6709\u53d8\u5316\uff0c\u4e0b\u8c03\u8bc4\u7ea7\u4e5f\u4f1a\u538b\u5236\u5e02\u573a\u60c5\u7eea\u3002",
    "guidance_raise": "\u7ba1\u7406\u5c42\u4e0a\u8c03\u76c8\u5229\u9884\u671f\uff0c\u5f80\u5f80\u5e26\u52a8\u5206\u6790\u5e08\u540c\u6b65\u4e0a\u8c03\u4f30\u503c\u3002",
    "guidance_cut": "\u4e0b\u8c03\u6307\u5f15\u662f\u9700\u6c42\u8d70\u5f31\u6216\u5229\u6da6\u7387\u627f\u538b\u7684\u65e9\u671f\u4fe1\u53f7\u3002",
    "fda_approval": "\u76d1\u7ba1\u6279\u51c6\u89e3\u9501\u65b0\u7684\u6536\u5165\u6765\u6e90\uff0c\u5e76\u6d88\u9664\u4e00\u9879\u91cd\u5927\u4e0d\u786e\u5b9a\u6027\u3002",
    "tax_credit": "\u653f\u7b56\u652f\u6301\u53ef\u6539\u5584\u6574\u4e2a\u884c\u4e1a\u7684\u7a0e\u540e\u5229\u6da6\u7387\u3002",
    "supply_chain": "\u539f\u6750\u6599\u77ed\u7f3a\u4e0e\u7269\u6d41\u5ef6\u8bef\u538b\u7f29\u5229\u6da6\u7387\u5e76\u5236\u7ea6\u4ea7\u91cf\u3002",
    "demand_surge": "\u7ec8\u7aef\u9700\u6c42\u4e0a\u5347\u652f\u6301\u5b9a\u4ef7\u80fd\u529b\u4e0e\u9500\u91cf\u589e\u957f\u3002",
    "labor_strike": "\u505c\u5de5\u51cf\u5c11\u4ea7\u51fa\uff0c\u5e76\u53ef\u80fd\u63a8\u9ad8\u5de5\u8d44\u4e0e\u6210\u672c\u3002",
    "policy_easing": "\u5229\u7387\u4e0b\u964d\u964d\u4f4e\u672a\u6765\u73b0\u91d1\u6d41\u7684\u6298\u73b0\u7387\uff0c\u9f13\u52b1\u98ce\u9669\u504f\u597d\u3002",
    "inflation_surprise": "\u8d85\u9884\u671f\u901a\u80c0\u8feb\u4f7f\u5e02\u573a\u5b9a\u4ef7\u66f4\u7d27\u7684\u8d27\u5e01\u653f\u7b56\u3002",
    "geopolitical_risk": "\u5168\u7403\u4e0d\u786e\u5b9a\u6027\u4e0a\u5347\uff0c\u63a8\u9ad8\u5404\u7c7b\u8d44\u4ea7\u7684\u907f\u9669\u6ea2\u4ef7\u3002",
    "consumer_confidence": "\u6d88\u8d39\u8005\u4fe1\u5fc3\u6539\u5584\u652f\u6301\u53ef\u9009\u6d88\u8d39\u4e0e\u4f01\u4e1a\u76c8\u5229\u3002",
    "volume_spike": "\u6210\u4ea4\u653e\u5927\u901a\u5e38\u610f\u5473\u7740\u591a\u7a7a\u529b\u91cf\u6b63\u5728\u53d1\u751f\u8f6c\u53d8\u3002",
    "rate_hike": "\u5229\u7387\u4e0a\u5347\u4f1a\u63d0\u9ad8\u672a\u6765\u76c8\u5229\u7684\u6298\u73b0\u7387\uff0c\u901a\u5e38\u538b\u7f29\u4f30\u503c\u3002",
    "rate_cut": "\u5229\u7387\u4e0b\u964d\u4f1a\u964d\u4f4e\u6298\u73b0\u7387\uff0c\u652f\u6491\u66f4\u9ad8\u7684\u4f30\u503c\u500d\u6570\u3002",
    "replay_gain": "\u5f53\u65e5\u6da8\u8dcc\u76f4\u63a5\u6765\u81ea\u771f\u5b9e A \u80a1\u5386\u53f2\u6570\u636e\u3002",
    "replay_loss": "\u5f53\u65e5\u6da8\u8dcc\u76f4\u63a5\u6765\u81ea\u771f\u5b9e A \u80a1\u5386\u53f2\u6570\u636e\u3002",
}


def generate_events(db: Session, day: int, rng: random.Random, stocks, state) -> list[models.NewsEvent]:
    pool = _event_pool()
    if state.market_cycle in ("bear", "recession"):
        count = rng.choices([1, 2, 3], weights=[0.4, 0.4, 0.2])[0]
    else:
        count = rng.choices([1, 2], weights=[0.65, 0.35])[0]

    by_industry = defaultdict(list)
    for stock in stocks:
        by_industry[stock.industry].append(stock)

    events = []
    for _ in range(count):
        category, scope, lo, hi, kind = rng.choice(pool)
        impact = rng.uniform(lo, hi)
        if scope == "stock":
            if kind == "fda_approval":
                candidates = by_industry["healthcare"]
            else:
                candidates = stocks
            stock = rng.choice(candidates)
            headline = EVENT_HEADLINES[kind].format(name=stock.name)
            event = models.NewsEvent(
                day=day,
                headline=headline,
                summary=EVENT_SUMMARIES[kind],
                category=category,
                scope="stock",
                kind=kind,
                stock_id=stock.id,
                impact_pct=impact,
            )
        elif scope == "industry":
            industry = rng.choice(INDUSTRIES)
            headline = EVENT_HEADLINES[kind].format(industry=industry.title())
            event = models.NewsEvent(
                day=day,
                headline=headline,
                summary=EVENT_SUMMARIES[kind],
                category=category,
                scope="industry",
                kind=kind,
                industry=industry,
                impact_pct=impact,
            )
        else:
            headline = EVENT_HEADLINES[kind]
            event = models.NewsEvent(
                day=day,
                headline=headline,
                summary=EVENT_SUMMARIES[kind],
                category=category,
                scope="market",
                kind=kind,
                impact_pct=impact,
            )
        db.add(event)
        events.append(event)
    return events


def _update_style(state: models.GameState, rng: random.Random) -> None:
    bias = {
        "bull": 0.0006,
        "recovery": 0.0004,
        "bear": -0.0002,
        "recession": -0.0008,
    }[state.market_cycle]
    state.style_factor = clamp(
        state.style_factor * 0.9 + bias * 0.4 + rng.gauss(0.0, 0.0025),
        -0.012,
        0.012,
    )


def _update_macro(
    db: Session,
    state: models.GameState,
    rng: random.Random,
    events: list[models.NewsEvent],
) -> float:
    """Mean-reverting inflation plus occasional central bank policy moves."""
    state.inflation = clamp(
        state.inflation + (2.5 - state.inflation) * 0.03 + rng.gauss(0.0, 0.25),
        0.5,
        8.0,
    )
    if state.day < state.next_rate_day:
        return 0.0

    target = policy_target_rate(state.inflation, state.market_cycle)
    diff = target - state.policy_rate
    step = 0.5 if abs(diff) > 2.0 else 0.25
    step = step if diff > 0 else -step
    probability = min(0.9, 0.35 + abs(diff) * 0.15)
    if abs(diff) >= 0.25 and rng.random() < probability:
        state.policy_rate = round(clamp(state.policy_rate + step, 0.25, 12.0), 2)
        is_cut = step < 0
        kind = "rate_cut" if is_cut else "rate_hike"
        impact = round(rng.uniform(0.0025, 0.005), 4)
        event = models.NewsEvent(
            day=state.day,
            headline=EVENT_HEADLINES[kind],
            summary=EVENT_SUMMARIES[kind],
            category="positive" if is_cut else "negative",
            scope="market",
            kind=kind,
            impact_pct=impact,
        )
        db.add(event)
        events.append(event)
        return impact if is_cut else -impact
    state.next_rate_day = state.day + rng.randint(15, 30)
    return 0.0


def _run_earnings(
    db: Session,
    state: models.GameState,
    stocks: list[models.Stock],
    rng: random.Random,
    events: list[models.NewsEvent],
    stock_shocks: dict[int, float],
) -> None:
    """Quarterly reports: estimate vs. actual, surprise, and price reaction."""
    for stock in stocks:
        if stock.next_earnings_day != state.day:
            continue
        estimate = stock.eps_estimate
        sigma = 0.05 + (1.0 - stock.earnings_quality) * 0.12
        surprise = clamp(rng.gauss(0.0, sigma), -0.4, 0.45)
        actual = max(0.01, estimate * (1.0 + surprise))
        reaction = clamp(surprise * 1.4 + rng.gauss(0.0, 0.012), -0.12, 0.12)

        stock.eps_estimate = round(actual, 4)
        stock.eps_actual = round(actual, 4)
        stock.earnings_growth = clamp(
            stock.earnings_growth + surprise * 0.35, 0.0, 0.5
        )
        stock.last_surprise_pct = round(surprise * 100.0, 2)
        stock.next_earnings_day = state.day + 63

        beat = surprise >= 0
        kind = "earnings_beat" if beat else "earnings_miss"
        event = models.NewsEvent(
            day=state.day,
            headline=EVENT_HEADLINES[kind].format(name=stock.name),
            summary=EVENT_SUMMARIES[kind],
            category="positive" if beat else "negative",
            scope="stock",
            kind=kind,
            stock_id=stock.id,
            impact_pct=round(abs(reaction), 4),
        )
        db.add(event)
        events.append(event)
        stock_shocks[stock.id] += reaction
        db.add(
            models.EarningsReport(
                stock_id=stock.id,
                day=state.day,
                eps_estimate=round(estimate, 4),
                eps_actual=round(actual, 4),
                surprise_pct=round(surprise * 100.0, 2),
                reaction_pct=round(reaction * 100.0, 2),
            )
        )


def _derive_cycle(stocks: list[models.Stock]) -> str:
    moments = [stock.momentum_20d or 0.0 for stock in stocks]
    avg = sum(moments) / len(moments) if moments else 0.0
    if avg > 0.05:
        return "bull"
    if avg > 0.01:
        return "recovery"
    if avg > -0.03:
        return "bear"
    return "recession"


def _replay_news(db: Session, state: models.GameState, gainer, loser) -> list[models.NewsEvent]:
    events = []
    pairs = []
    if gainer:
        pairs.append((gainer[1], gainer[0], "replay_gain", "positive"))
    if loser:
        pairs.append((loser[1], loser[0], "replay_loss", "negative"))
    for stock, ret, kind, category in pairs:
        event = models.NewsEvent(
            day=state.day,
            headline="",
            summary="",
            category=category,
            scope="stock",
            kind=kind,
            stock_id=stock.id,
            impact_pct=round(abs(ret), 4),
        )
        db.add(event)
        events.append(event)
    return events


def _run_counterplay(db: Session, state: models.GameState, stocks: list) -> None:
    price_by_id = {stock.id: stock.price for stock in stocks}
    stock_by_id = {stock.id: stock for stock in stocks}
    for player in db.query(models.Player).all():
        holdings = (
            db.query(models.Holding)
            .filter(models.Holding.player_id == player.id)
            .all()
        )
        if not holdings:
            continue
        total = player.cash + sum(
            holding.shares * price_by_id.get(holding.stock_id, 0.0)
            for holding in holdings
        )
        if total <= 0:
            continue
        best = max(
            holdings,
            key=lambda holding: holding.shares * price_by_id.get(holding.stock_id, 0.0),
        )
        stock = stock_by_id.get(best.stock_id)
        if stock is None or stock.price <= 0:
            continue
        holding_value = best.shares * stock.price
        if holding_value / total < 0.12:
            continue
        notional = min(holding_value * 0.03, stock.price * stock.avg_volume * 0.05)
        impact = flow_impact(notional, stock.avg_volume, stock.price)
        stock.price = round(max(0.01, stock.price * (1 - impact)), 4)
        stock.volume += int(notional / max(0.01, stock.price))
        refresh_book(stock, state)
        db.add(
            models.NewsEvent(
                day=state.day,
                headline="{name} faces quiet distribution",
                summary="counterplay",
                category="negative",
                scope="stock",
                kind="counterplay",
                stock_id=stock.id,
                impact_pct=round(-impact * 100, 2),
            )
        )


def advance_day(db: Session, rng: random.Random | None = None) -> dict:
    """Advance one trading day by replaying the next real A-share daily row."""
    rng = rng or random.Random(SEED + db.query(models.GameState).first().day)
    state = db.query(models.GameState).first()
    stocks = db.query(models.Stock).order_by(models.Stock.id).all()

    state.market_cycle = _derive_cycle(stocks)
    avg_momentum = sum(stock.momentum_20d or 0.0 for stock in stocks) / len(stocks)
    state.sentiment = clamp(1.0 + avg_momentum * 4.0, 0.55, 1.5)
    state.style_factor = clamp(
        state.style_factor * 0.9 + rng.gauss(0.0, 0.0025), -0.012, 0.012
    )

    _, bot_volume = tick_bots(db, state, stocks, rng)

    replay = replay_rows()
    cursor = state.replay_index
    idx_row = index_row(cursor)
    new_date = idx_row["d"]
    state.shanghai_prev = state.shanghai_index
    state.shanghai_index = round(idx_row["c"], 2)
    session_prev = {stock.id: stock.price for stock in stocks}
    closes_by_stock = {}
    dates_by_stock: dict[int, list[str]] = {}
    date_sets: dict[int, set[str]] = {}
    for stock in stocks:
        rows = (
            db.query(models.PriceHistory.trade_date, models.PriceHistory.close)
            .filter(models.PriceHistory.stock_id == stock.id)
            .order_by(models.PriceHistory.trade_date)
            .all()
        )
        dates_by_stock[stock.id] = [row[0] for row in rows]
        closes_by_stock[stock.id] = [row[1] for row in rows]
        date_sets[stock.id] = {row[0] for row in rows}

    returns = []
    gainer = None
    loser = None
    for stock in stocks:
        rows = replay[stock.ticker]
        row = rows[min(cursor, len(rows) - 1)]
        prev = session_prev[stock.id]
        close = row["c"]
        real_return = close / prev - 1.0 if prev else 0.0
        returns.append(real_return)
        if gainer is None or real_return > gainer[0]:
            gainer = (real_return, stock)
        if loser is None or real_return < loser[0]:
            loser = (real_return, stock)

        impact = stock.player_impact or 0.0
        stock.prev_close = round(prev, 2)
        stock.price = round(close * (1 + impact), 2)
        stock.player_impact = round(impact * 0.85, 6)
        stock.volume = int(row["v"]) + int(bot_volume.get(stock.id, 0))
        stock.avg_volume = int(stock.avg_volume * 0.9 + stock.volume * 0.1)
        stock.prev_daily_ret = real_return

        closes = closes_by_stock[stock.id]
        if row["d"] in date_sets[stock.id]:
            # The replay looped back to an already-stored date: overwrite it
            # instead of inserting a duplicate row.
            index = dates_by_stock[stock.id].index(row["d"])
            closes[index] = close
            all_closes = closes
            existing = (
                db.query(models.PriceHistory)
                .filter(
                    models.PriceHistory.stock_id == stock.id,
                    models.PriceHistory.trade_date == row["d"],
                )
                .first()
            )
            if existing is not None:
                existing.open = row["o"]
                existing.high = row["h"]
                existing.low = row["l"]
                existing.close = round(close, 2)
                existing.volume = stock.volume
        else:
            all_closes = closes + [close]
            db.add(
                models.PriceHistory(
                    stock_id=stock.id,
                    trade_date=row["d"],
                    open=row["o"],
                    high=row["h"],
                    low=row["l"],
                    close=round(close, 2),
                    volume=stock.volume,
                )
            )
        stock.momentum_20d = (
            close / all_closes[-21] - 1.0 if len(all_closes) >= 21 else 0.0
        )
        stock.momentum_60d = (
            close / all_closes[-61] - 1.0 if len(all_closes) >= 61 else 0.0
        )
        recent = all_closes[-253:]
        stock.fifty_two_week_high = max(recent)
        stock.fifty_two_week_low = min(recent)
        stock.eps_estimate = round(
            stock.eps_estimate
            * (1.0 + stock.earnings_growth * 0.6 / 252.0 + 0.001 * normal(rng)),
            4,
        )
        stock.fundamental_price = fundamental_price(
            stock, state.policy_rate, state.sentiment
        )
        stock.pe_ratio = clamp(close / annual_eps(stock), 1.0, 200.0)
        refresh_book(stock, state)
        stock.updated_at = models.utc_now()

    _run_counterplay(db, state, stocks)
    events = _replay_news(db, state, gainer, loser)

    state.benchmark_prev = state.benchmark_value
    avg_return = sum(returns) / len(returns) if returns else 0.0
    state.benchmark_value = round(state.benchmark_value * (1.0 + avg_return), 4)
    state.replay_index = next_replay_index(cursor)
    state.date = new_date
    state.day += 1

    refresh_rival_values(db, state.day)
    db.query(models.Holding).update({models.Holding.locked_shares: 0.0})
    player = db.query(models.Player).first()
    _snapshot_portfolio(db, player, state)
    db.commit()
    return {
        "day": state.day,
        "date": state.date,
        "market_cycle": state.market_cycle,
        "sentiment": round(state.sentiment, 4),
        "benchmark_value": state.benchmark_value,
        "events": len(events),
    }


def _snapshot_portfolio(db: Session, player: models.Player, state: models.GameState) -> None:
    if player is None:
        return
    holdings = db.query(models.Holding).filter(models.Holding.player_id == player.id).all()
    invested = 0.0
    for holding in holdings:
        stock = db.get(models.Stock, holding.stock_id)
        invested += holding.shares * stock.price
    total = player.cash + invested
    db.add(
        models.PortfolioHistory(
            player_id=player.id,
            day=state.day,
            date=state.date,
            value=round(total, 2),
            cash=round(player.cash, 2),
            invested=round(invested, 2),
        )
    )
