from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..i18n import get_lang
from ..services.auth import get_current_player
from ..services import portfolio

router = APIRouter(prefix="/api", tags=["portfolio"])


@router.get("/portfolio")
def get_portfolio(request: Request, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    lang = get_lang(request)
    return {
        "summary": portfolio.portfolio_summary(db, player),
        "holdings": portfolio.holdings_detail(db, player, lang),
        "allocation": portfolio.allocation(db, player),
        "performance": portfolio.performance(db, player),
        "transactions": portfolio.transaction_history(db, player, 20, lang),
    }
