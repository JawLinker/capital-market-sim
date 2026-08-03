def test_dark_pool_fills_at_midpoint_without_impact(client):
    from app import models
    from app.database import SessionLocal

    db = SessionLocal()
    stock = db.query(models.Stock).first()
    ticker = stock.ticker
    mid = round((stock.bid + stock.ask) / 2.0, 2)
    price_before = stock.price
    impact_before = stock.player_impact or 0.0
    volume_before = stock.volume
    db.close()

    trade = client.post(
        "/api/trades",
        json={
            "action": "buy",
            "ticker": ticker,
            "shares": 10,
            "dark_pool": True,
        },
    ).json()["trade"]
    assert trade["dark_pool"] is True
    assert trade["price"] == mid

    db = SessionLocal()
    stock = db.query(models.Stock).filter(models.Stock.ticker == ticker).first()
    assert stock.price == price_before
    assert (stock.player_impact or 0.0) == impact_before
    assert stock.volume == volume_before
    db.close()


def test_dark_pool_rejects_oversized_order(client):
    from app import models
    from app.database import SessionLocal

    db = SessionLocal()
    player = db.query(models.Player).first()
    stock = db.query(models.Stock).first()
    db.add(
        models.Holding(
            player_id=player.id,
            stock_id=stock.id,
            shares=1_000_000_000.0,
            avg_cost=10.0,
        )
    )
    db.commit()
    db.close()

    response = client.post(
        "/api/trades",
        json={
            "action": "sell",
            "ticker": stock.ticker,
            "shares": 1_000_000_000,
            "dark_pool": True,
        },
    )
    assert response.status_code == 400


def test_dragon_tiger_excludes_dark_trades(client):
    from app import models
    from app.database import SessionLocal
    from app.services.dragon_tiger import today_board

    db = SessionLocal()
    player = db.query(models.Player).first()
    stock = db.query(models.Stock).first()
    db.add(
        models.Transaction(
            player_id=player.id,
            stock_id=stock.id,
            action="buy",
            shares=100,
            price=10,
            gross=1000,
            fee=1,
            stamp_tax=0,
            net=999,
            realized_pnl=0,
            day=0,
            dark_pool=1,
        )
    )
    db.add(
        models.Transaction(
            player_id=player.id,
            stock_id=stock.id,
            action="sell",
            shares=100,
            price=10,
            gross=1000,
            fee=1,
            stamp_tax=0,
            net=999,
            realized_pnl=0,
            day=0,
            dark_pool=0,
        )
    )
    db.commit()
    db.close()

    board = today_board(SessionLocal(), 0, "en")
    assert any(item["ticker"] == stock.ticker and item["net"] < 0 for item in board)
