def test_dividend_pays_cash_and_adjusts_price(client):
    from app import models
    from app.database import SessionLocal
    from app.services.dividends import _dividend_date, process_dividends

    db = SessionLocal()
    player = db.query(models.Player).first()
    stock = db.query(models.Stock).first()
    state = db.query(models.GameState).first()
    state.date = _dividend_date(stock.id, 2021)
    db.add(
        models.Holding(
            player_id=player.id,
            stock_id=stock.id,
            shares=100.0,
            avg_cost=10.0,
        )
    )
    cash_before = player.cash
    price_before = stock.price
    db.commit()
    db.close()

    results = process_dividends(SessionLocal())
    assert results

    db = SessionLocal()
    player = db.query(models.Player).first()
    stock = db.query(models.Stock).first()
    assert player.cash > cash_before
    assert stock.price < price_before
    assert (
        db.query(models.NewsEvent)
        .filter(models.NewsEvent.kind == "dividend")
        .count()
        >= 1
    )
    db.close()


def test_advance_response_has_market_summary(client):
    body = client.post("/api/game/advance", json={"days": 1}).json()
    assert "market_summary" in body
    assert "northbound_flow" in body["market_summary"]
    assert body["market_summary"]["gainers"]
    assert "dividends" in body
