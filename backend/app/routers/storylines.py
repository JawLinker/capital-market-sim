from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..i18n import get_lang
from ..services import portfolio
from ..services.auth import get_current_player
from ..services.storylines import get_storylines

router = APIRouter(prefix="/api", tags=["storylines"])


@router.get("/storylines")
def list_storylines(request: Request, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    return get_storylines(db, player, get_lang(request))
