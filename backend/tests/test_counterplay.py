def test_counterplay_pressures_overexposed_player(client):
    from app import models
    from app.database import SessionLocal

    db = SessionLocal()
    player = db.query(models.Player).first()
    stock = db.query(models.Stock).order_by(models.Stock.market_cap.desc()).first()
    db.add(
        models.Holding(
            player_id=player.id,
            stock_id=stock.id,
            shares=1_000_000.0,
            avg_cost=10.0,
        )
    )
    db.commit()
    db.close()

    client.post("/api/game/advance")

    db = SessionLocal()
    count = (
        db.query(models.NewsEvent)
        .filter(models.NewsEvent.kind == "counterplay")
        .count()
    )
    db.close()
    assert count >= 1


def test_dragon_tiger_appears_after_advance(client):
    client.post("/api/game/advance")
    state = client.get("/api/state").json()
    board = state["market"]["dragon_tiger"]
    assert isinstance(board, list)
    assert len(board) > 0
    item = board[0]
    assert item["name"]
    assert item["buy_seat"]
    assert item["sell_seat"]
    assert "net" in item
