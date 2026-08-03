from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..services import portfolio
from ..services.auth import get_current_player
from ..services.decisions import apply_era_bonus, resolve_decision

router = APIRouter(prefix="/api", tags=["decisions"])


class DecisionRequest(BaseModel):
    option_key: str = Field(min_length=1, max_length=32)


class EraBonusRequest(BaseModel):
    grade_key: str = Field(min_length=1, max_length=16)
    option_key: str = Field(min_length=1, max_length=32)


@router.post("/decisions/{decision_id}/resolve")
def resolve(
    decision_id: int,
    request: Request,
    body: DecisionRequest,
    db: Session = Depends(get_db),
):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    try:
        return resolve_decision(db, player, decision_id, body.option_key)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/decisions/era-bonus")
def era_bonus(request: Request, body: EraBonusRequest, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    try:
        return apply_era_bonus(db, player, body.grade_key, body.option_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
