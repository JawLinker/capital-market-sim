from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..services import portfolio
from ..services.auth import get_current_player
from ..services.duels import create_duel, list_duels

router = APIRouter(prefix="/api", tags=["duels"])


class DuelRequest(BaseModel):
    rival_id: int
    stake: float = Field(gt=0)
    days: int = Field(ge=1, le=60)


@router.post("/duels")
def create(request: Request, body: DuelRequest, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    rival = db.get(models.Rival, body.rival_id)
    if rival is None:
        raise HTTPException(status_code=404, detail="Rival not found")
    try:
        duel = create_duel(db, player, rival, body.stake, body.days)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"duel": {"id": duel.id, "rival": rival.name, "stake": duel.stake}}


@router.get("/duels")
def get_duels(request: Request, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    return {"duels": list_duels(db, player)}
