from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..services import portfolio
from ..services.auth import get_current_player
from ..services.margin import repay_margin

router = APIRouter(prefix="/api", tags=["margin"])


class RepayRequest(BaseModel):
    amount: float = Field(gt=0)


@router.post("/margin/repay")
def repay(request: Request, body: RepayRequest, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    try:
        return repay_margin(db, player, body.amount)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
