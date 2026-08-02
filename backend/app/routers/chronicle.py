from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..i18n import get_lang
from ..services import portfolio
from ..services.auth import get_current_player
from ..services.chronicle import build_chronicle

router = APIRouter(prefix="/api", tags=["chronicle"])


@router.get("/chronicle")
def get_chronicle(request: Request, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    state = db.query(models.GameState).first()
    date = state.date if state else "2019-03-04"
    return build_chronicle(db, player, date, get_lang(request))
