def test_leveraged_buy_uses_margin(client):
    from app import models
    from app.database import SessionLocal

    trade = client.post(
        "/api/trades",
        json={
            "action": "buy",
            "ticker": "BCSC",
            "shares": 1_000_000,
            "leverage": 2,
        },
    ).json()["trade"]
    assert trade["shares"] > 1000

    db = SessionLocal()
    player = db.query(models.Player).first()
    assert (player.margin_debt or 0.0) > 0
    db.close()


def test_margin_interest_accrues(client):
    from app import models
    from app.database import SessionLocal

    client.post(
        "/api/trades",
        json={
            "action": "buy",
            "ticker": "BCSC",
            "shares": 1_000_000,
            "leverage": 2,
        },
    )
    db = SessionLocal()
    player = db.query(models.Player).first()
    debt_before = player.margin_debt
    db.close()

    client.post("/api/game/advance")

    db = SessionLocal()
    player = db.query(models.Player).first()
    assert player.margin_debt > debt_before
    db.close()


def test_forced_liquidation(client):
    from app import models
    from app.database import SessionLocal

    db = SessionLocal()
    player = db.query(models.Player).first()
    stock = db.query(models.Stock).first()
    player.cash = 0.0
    player.margin_debt = 100_000.0
    db.add(
        models.Holding(
            player_id=player.id,
            stock_id=stock.id,
            shares=800,
            avg_cost=10.0,
        )
    )
    db.commit()
    db.close()

    body = client.post("/api/game/advance").json()
    results = body.get("margin_results", [])
    assert results and results[0]["forced"] is True

    db = SessionLocal()
    holdings = (
        db.query(models.Holding)
        .filter(models.Holding.player_id == player.id)
        .count()
    )
    assert holdings == 0
    db.close()
