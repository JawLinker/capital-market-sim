from fastapi import APIRouter, Depends, Request
from fastapi import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..i18n import get_lang
from ..services import portfolio
from ..services.auth import get_current_player
from ..services.quests import commission, daily_challenge
from ..services.quests import resolve_commission_decision

router = APIRouter(prefix="/api", tags=["quests"])


class CommissionResolveRequest(BaseModel):
    option_key: str = Field(min_length=1, max_length=32)


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


@router.post("/quests/commission/{decision_id}/resolve")
def resolve_commission(
    decision_id: int,
    request: Request,
    body: CommissionResolveRequest,
    db: Session = Depends(get_db),
):
    try:
        return resolve_commission_decision(
            db,
            _player(db, request),
            decision_id,
            body.option_key,
            get_lang(request),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
