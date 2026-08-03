"""Margin financing: daily interest and forced liquidation below 130%."""

from sqlalchemy.orm import Session

from .. import models
from .orderbook import execute_market_order
from .portfolio import portfolio_value

ANNUAL_RATE = 0.06
FORCE_RATIO = 1.3
RECOVER_RATIO = 1.5


def process_margin(db: Session) -> list:
    state = db.query(models.GameState).first()
    results = []
    for player in db.query(models.Player).all():
        debt = player.margin_debt or 0.0
        if debt <= 0:
            continue
        debt = round(debt * (1.0 + ANNUAL_RATE / 252.0), 2)
        player.margin_debt = debt
        value = portfolio_value(db, player)
        ratio = value / debt if debt else 999.0
        sold = []
        if ratio >= FORCE_RATIO:
            if player.margin_call_day >= 0:
                player.margin_call_day = -1
                player.margin_call_deadline = -1
            continue
        if player.margin_call_day < 0:
            player.margin_call_day = state.day
            player.margin_call_deadline = state.day + 3
            results.append(
                {
                    "player_id": player.id,
                    "margin_call": True,
                    "days_left": 3,
                    "ratio": round(ratio, 2),
                }
            )
            continue
        if state.day < player.margin_call_deadline:
            results.append(
                {
                    "player_id": player.id,
                    "margin_call": True,
                    "days_left": player.margin_call_deadline - state.day,
                    "ratio": round(ratio, 2),
                }
            )
            continue
        if ratio < FORCE_RATIO:
            holdings = (
                db.query(models.Holding, models.Stock)
                .join(models.Stock, models.Holding.stock_id == models.Stock.id)
                .filter(models.Holding.player_id == player.id)
                .all()
            )
            holdings.sort(
                key=lambda item: item[0].shares * item[1].price,
                reverse=True,
            )
            while ratio < RECOVER_RATIO and holdings:
                holding, stock = holdings.pop(0)
                exec_price = execute_market_order(
                    db,
                    stock,
                    state,
                    holding.shares,
                    "sell",
                )
                if exec_price is None:
                    continue
                gross = round(holding.shares * exec_price, 2)
                fee = round(max(1.0, gross * 0.0015), 2)
                stamp_tax = round(gross * 0.0005, 2)
                net = round(gross - fee - stamp_tax, 2)
                realized = round(
                    (exec_price - holding.avg_cost) * holding.shares - fee - stamp_tax,
                    2,
                )
                player.cash = round(player.cash + net, 2)
                db.add(
                    models.Transaction(
                        player_id=player.id,
                        stock_id=stock.id,
                        action="sell",
                        shares=holding.shares,
                        price=round(exec_price, 2),
                        gross=gross,
                        fee=fee,
                        stamp_tax=stamp_tax,
                        net=net,
                        realized_pnl=realized,
                        day=state.day,
                    )
                )
                sold.append(
                    {
                        "name": stock.name,
                        "proceeds": net,
                    }
                )
                db.delete(holding)
                db.flush()
                value = portfolio_value(db, player)
                ratio = value / debt if debt else 999.0
            results.append(
                {
                    "player_id": player.id,
                    "forced": True,
                    "ratio": round(ratio, 2),
                    "sold": sold,
                }
            )
            player.margin_call_day = -1
            player.margin_call_deadline = -1
    db.commit()
    return results


def repay_margin(db: Session, player: models.Player, amount: float) -> dict:
    amount = round(amount, 2)
    debt = player.margin_debt or 0.0
    if amount <= 0:
        raise ValueError("Repayment amount must be positive")
    affordable = min(amount, player.cash, debt)
    if affordable <= 0:
        raise ValueError("No cash or debt to repay")
    player.cash = round(player.cash - affordable, 2)
    player.margin_debt = round(debt - affordable, 2)
    db.commit()
    return {"repaid": affordable, "margin_debt": player.margin_debt}
