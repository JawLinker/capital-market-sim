from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import ChatRequest
from ..i18n import get_lang
from ..services.auth import get_current_player
from ..services import portfolio
from ..services.advisor import chat, portfolio_report

router = APIRouter(prefix="/api/advisor", tags=["advisor"])


@router.get("/portfolio")
def advisor_report(request: Request, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    return portfolio_report(db, player, get_lang(request))


@router.post("/chat")
def advisor_chat(request: Request, body: ChatRequest, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    return chat(db, player, body.message, get_lang(request))
