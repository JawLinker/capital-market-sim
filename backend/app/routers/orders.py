from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..services import portfolio
from ..services.auth import get_current_player
from ..services.pending_orders import (
    cancel_pending_order,
    create_pending_order,
    list_pending_orders,
)

router = APIRouter(prefix="/api", tags=["orders"])


class OrderRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=8)
    kind: str = Field(min_length=1, max_length=20)
    price: float = Field(gt=0)
    shares: float = Field(gt=0)


@router.post("/orders")
def create_order(request: Request, body: OrderRequest, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    stock = (
        db.query(models.Stock)
        .filter(models.Stock.ticker == body.ticker.upper())
        .first()
    )
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    try:
        order = create_pending_order(
            db,
            player,
            stock,
            body.kind,
            body.price,
            body.shares,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"order": {"id": order.id, "ticker": stock.ticker, "kind": order.kind}}


@router.get("/orders")
def get_orders(request: Request, db: Session = Depends(get_db)):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    return {"orders": list_pending_orders(db, player)}


@router.post("/orders/{order_id}/cancel")
def cancel_order(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    player = get_current_player(db, request) or portfolio.get_or_create_player(db)
    if not cancel_pending_order(db, player, order_id):
        raise HTTPException(status_code=404, detail="Open order not found")
    return {"status": "cancelled"}
