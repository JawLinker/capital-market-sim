from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..i18n import company_name, get_lang

router = APIRouter(prefix="/api", tags=["earnings"])


@router.get("/earnings")
def list_earnings(
    request: Request,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
):
    lang = get_lang(request)
    rows = (
        db.query(models.EarningsReport)
        .order_by(models.EarningsReport.id.desc())
        .limit(limit)
        .all()
    )
    result = []
    for row in reversed(rows):
        stock = db.get(models.Stock, row.stock_id)
        result.append(
            {
                "id": row.id,
                "day": row.day,
                "ticker": stock.ticker,
                "company": company_name(lang, stock.ticker, stock.name),
                "eps_estimate": row.eps_estimate,
                "eps_actual": row.eps_actual,
                "surprise_pct": row.surprise_pct,
                "reaction_pct": row.reaction_pct,
            }
        )
    return {"earnings": result}
