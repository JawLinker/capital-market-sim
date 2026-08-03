"""Limit, stop-loss, and take-profit orders that fill as the market moves."""

from sqlalchemy.orm import Session

from .. import models
from . import portfolio

VALID_KINDS = {"buy_limit", "sell_limit", "stop_loss", "take_profit"}


def create_pending_order(
    db: Session,
    player: models.Player,
    stock: models.Stock,
    kind: str,
    price: float,
    shares: float,
) -> models.PendingOrder:
    if kind not in VALID_KINDS:
        raise ValueError("Unsupported order kind")
    price = round(price, 2)
    shares = round(shares, 4)
    if price <= 0 or shares <= 0 or shares * price < 10:
        raise ValueError("Invalid limit price or order size")
    state = db.query(models.GameState).first()
    order = models.PendingOrder(
        player_id=player.id,
        stock_id=stock.id,
        kind=kind,
        price=price,
        shares=shares,
        created_day=state.day,
    )
    db.add(order)
    db.commit()
    return order


def cancel_pending_order(db: Session, player: models.Player, order_id: int) -> bool:
    order = (
        db.query(models.PendingOrder)
        .filter(
            models.PendingOrder.id == order_id,
            models.PendingOrder.player_id == player.id,
            models.PendingOrder.status == "open",
        )
        .first()
    )
    if order is None:
        return False
    order.status = "cancelled"
    db.commit()
    return True


def list_pending_orders(db: Session, player: models.Player) -> list:
    rows = (
        db.query(models.PendingOrder, models.Stock)
        .join(models.Stock, models.PendingOrder.stock_id == models.Stock.id)
        .filter(models.PendingOrder.player_id == player.id)
        .order_by(models.PendingOrder.id.desc())
        .all()
    )
    return [
        {
            "id": order.id,
            "ticker": stock.ticker,
            "name": stock.name,
            "kind": order.kind,
            "price": order.price,
            "shares": order.shares,
            "status": order.status,
            "created_day": order.created_day,
            "filled_day": order.filled_day,
        }
        for order, stock in rows
    ]


def execute_pending_orders(db: Session) -> int:
    state = db.query(models.GameState).first()
    orders = (
        db.query(models.PendingOrder)
        .filter(models.PendingOrder.status == "open")
        .order_by(models.PendingOrder.id)
        .all()
    )
    filled = 0
    for order in orders:
        stock = db.get(models.Stock, order.stock_id)
        player = db.get(models.Player, order.player_id)
        if stock is None or player is None:
            order.status = "cancelled"
            continue
        price = stock.price
        action = None
        if order.kind == "buy_limit" and price <= order.price:
            action = "buy"
        elif order.kind == "sell_limit" and price >= order.price:
            action = "sell"
        elif order.kind == "stop_loss" and price <= order.price:
            action = "sell"
        elif order.kind == "take_profit" and price >= order.price:
            action = "sell"
        if action is None:
            continue
        try:
            portfolio.execute_trade(db, player, stock, action, order.shares)
            order.status = "filled"
            order.filled_day = state.day
            filled += 1
        except ValueError:
            continue
    db.commit()
    return filled
