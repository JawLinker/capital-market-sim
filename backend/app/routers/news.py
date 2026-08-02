from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..i18n import company_name, get_lang, industry_label
from ..services.market_engine import (
    EVENT_HEADLINES,
    EVENT_HEADLINES_ZH,
    EVENT_SUMMARIES,
    EVENT_SUMMARIES_ZH,
)

router = APIRouter(prefix="/api", tags=["news"])


@router.get("/news")
def list_news(
    request: Request,
    limit: int = Query(default=25, le=100),
    scope: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(models.NewsEvent)
    if scope in ("stock", "industry", "market"):
        query = query.filter(models.NewsEvent.scope == scope)
    rows = query.order_by(models.NewsEvent.id.desc()).limit(limit).all()
    lang = get_lang(request)
    result = []
    for row in reversed(rows):
        stock = db.get(models.Stock, row.stock_id) if row.stock_id else None
        if row.kind:
            headline_kwargs = {}
            if row.scope == "stock" and stock:
                headline_kwargs["name"] = company_name(lang, stock.ticker, stock.name)
                if row.kind in ("replay_gain", "replay_loss"):
                    headline_kwargs["pct"] = row.impact_pct * 100.0
            elif row.scope == "industry" and row.industry:
                headline_kwargs["industry"] = industry_label(lang, row.industry)
            if lang == "zh":
                headline = EVENT_HEADLINES_ZH.get(row.kind, row.headline).format(
                    **headline_kwargs
                )
                summary = EVENT_SUMMARIES_ZH.get(row.kind, row.summary)
            else:
                headline = EVENT_HEADLINES.get(row.kind, row.headline).format(
                    **headline_kwargs
                )
                summary = EVENT_SUMMARIES.get(row.kind, row.summary)
        else:
            headline = row.headline
            summary = row.summary
        result.append(
            {
                "id": row.id,
                "day": row.day,
                "headline": headline,
                "summary": summary,
                "category": row.category,
                "scope": row.scope,
                "ticker": stock.ticker if stock else None,
                "company": company_name(lang, stock.ticker, stock.name) if stock else None,
                "industry": row.industry,
                "industry_label": industry_label(lang, row.industry) if row.industry else None,
                "impact_pct": row.impact_pct,
            }
        )
    return {"news": result}
