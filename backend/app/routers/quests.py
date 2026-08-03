from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..i18n import get_lang
from ..services import portfolio
from ..services.auth import get_current_player
from ..services.quests import commission, daily_challenge

router = APIRouter(prefix="/api", tags=["quests"])


def _player(db: Session, request: Request):
    return get_current_player(db, request) or portfolio.get_or_create_player(db)


@router.get("/quests/daily")
def get_daily(request: Request, db: Session = Depends(get_db)):
    return daily_challenge(db, _player(db, request), get_lang(request))


@router.get("/quests/commission")
def get_commission(request: Request, db: Session = Depends(get_db)):
    state = db.query(models.GameState).first()
    if state is None:
        raise RuntimeError("Game state missing")
    return commission(db, _player(db, request), state, get_lang(request))
