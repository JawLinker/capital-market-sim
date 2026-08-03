"""Collect giant-company earnings headlines into a newspaper-style popup."""

from sqlalchemy.orm import Session

from .. import models
from ..i18n import company_name
from .market_engine import (
    EVENT_HEADLINES,
    EVENT_HEADLINES_ZH,
    EVENT_SUMMARIES,
    EVENT_SUMMARIES_ZH,
)

EARNINGS_KINDS = {"earnings_beat", "earnings_miss"}


def collect_newspaper(db: Session, day: int, lang: str) -> list:
    stocks = db.query(models.Stock).order_by(models.Stock.market_cap.desc()).all()
    if not stocks:
        return []
    giant_cutoff = stocks[min(9, len(stocks) - 1)].market_cap
    rows = (
        db.query(models.NewsEvent, models.Stock)
        .join(models.Stock, models.NewsEvent.stock_id == models.Stock.id)
        .filter(
            models.NewsEvent.day == day,
            models.NewsEvent.kind.in_(EARNINGS_KINDS),
            models.Stock.market_cap >= giant_cutoff,
        )
        .order_by(models.NewsEvent.id.desc())
        .limit(2)
        .all()
    )
    result = []
    for row, stock in rows:
        name = company_name(lang, stock.ticker, stock.name)
        if lang == "zh":
            headline = EVENT_HEADLINES_ZH.get(row.kind, row.headline).format(name=name)
            summary = EVENT_SUMMARIES_ZH.get(row.kind, row.summary)
        else:
            headline = EVENT_HEADLINES.get(row.kind, row.headline).format(name=name)
            summary = EVENT_SUMMARIES.get(row.kind, row.summary)
        result.append(
            {
                "ticker": stock.ticker,
                "name": name,
                "kind": row.kind,
                "headline": headline,
                "summary": summary,
                "impact_pct": row.impact_pct,
            }
        )
    return result
