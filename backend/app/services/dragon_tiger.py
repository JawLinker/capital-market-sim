"""The daily dragon-tiger board: who quietly bought and sold the hot names."""

from collections import defaultdict

from sqlalchemy.orm import Session

from .. import models
from ..i18n import company_name

SEATS = [
    "\u752c\u6c5f\u8def\u5e2d\u4f4d",
    "\u671b\u4eac\u8d44\u7ba1",
    "\u6731\u96c0\u574a",
    "\u6c49\u5510\u8bc1\u5238",
    "\u897f\u6e56\u57fa\u91d1",
    "\u6df1\u5357\u5927\u9053\u5e2d\u4f4d",
    "\u6ee8\u6c5f\u6e38\u8d44",
    "\u8001\u5e84\u4f1a\u9986",
]

SEATS_EN = [
    "Yongjiang Road Seat",
    "Wangjing Capital",
    "Zhuque Lane",
    "Hantang Securities",
    "West Lake Fund",
    "Shennan Avenue Seat",
    "Binjiang Hot Money",
    "Old Master's Hall",
]


def today_board(db: Session, day: int, lang: str) -> list:
    net = defaultdict(float)
    bot_trades = (
        db.query(models.BotTrade)
        .filter(models.BotTrade.day == day)
        .all()
    )
    transactions = (
        db.query(models.Transaction)
        .filter(models.Transaction.day == day)
        .all()
    )
    for row in bot_trades:
        amount = row.notional or row.shares * row.price
        net[row.stock_id] += amount if row.action == "buy" else -amount
    for row in transactions:
        if row.dark_pool:
            continue
        net[row.stock_id] += row.gross if row.action == "buy" else -row.gross
    ranked = sorted(net.items(), key=lambda item: -abs(item[1]))[:5]
    seats = SEATS_EN if lang != "zh" else SEATS
    result = []
    for index, (stock_id, amount) in enumerate(ranked):
        stock = db.get(models.Stock, stock_id)
        if stock is None:
            continue
        buyer = seats[(stock_id * 7 + index * 3) % len(seats)]
        seller = seats[(stock_id * 13 + index * 5 + 1) % len(seats)]
        result.append(
            {
                "ticker": stock.ticker,
                "name": company_name(lang, stock.ticker, stock.name),
                "net": round(amount, 2),
                "buy_seat": buyer if amount > 0 else seller,
                "sell_seat": seller if amount > 0 else buyer,
            }
        )
    return result
