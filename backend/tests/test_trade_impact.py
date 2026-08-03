def test_player_buy_moves_price(client):
    from app import models
    from app.database import SessionLocal

    db = SessionLocal()
    stock = (
        db.query(models.Stock)
        .filter(models.Stock.avg_volume < 5_000_000)
        .first()
    )
    ticker = stock.ticker
    price_before = stock.price
    impact_before = stock.player_impact or 0.0
    db.close()

    client.post(
        "/api/trades",
        json={"action": "buy", "ticker": ticker, "shares": 1_000_000},
    )

    db = SessionLocal()
    stock = db.query(models.Stock).filter(models.Stock.ticker == ticker).first()
    assert (stock.player_impact or 0.0) > impact_before
    assert stock.price > price_before
    db.close()


def test_player_impact_decays_after_advance(client):
    from app import models
    from app.database import SessionLocal

    db = SessionLocal()
    stock = (
        db.query(models.Stock)
        .filter(models.Stock.avg_volume < 5_000_000)
        .first()
    )
    ticker = stock.ticker
    db.close()

    client.post(
        "/api/trades",
        json={"action": "buy", "ticker": ticker, "shares": 1_000_000},
    )
    db = SessionLocal()
    stock = db.query(models.Stock).filter(models.Stock.ticker == ticker).first()
    impact_after_buy = stock.player_impact or 0.0
    db.close()

    client.post("/api/game/advance")

    db = SessionLocal()
    stock = db.query(models.Stock).filter(models.Stock.ticker == ticker).first()
    assert (stock.player_impact or 0.0) < impact_after_buy
    db.close()
