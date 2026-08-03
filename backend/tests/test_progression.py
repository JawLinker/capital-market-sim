def test_limit_order_fills_on_advance(client):
    client.post(
        "/api/orders",
        json={"ticker": "BCSC", "kind": "buy_limit", "price": 999999, "shares": 1},
    )
    orders = client.get("/api/orders").json()["orders"]
    assert orders[0]["status"] == "open"
    client.post("/api/game/advance")
    orders = client.get("/api/orders").json()["orders"]
    assert orders[0]["status"] == "filled"
    assert client.get("/api/replay").json()["stats"]["total_trades"] >= 1


def test_stop_loss_order_sells_on_advance(client):
    client.post("/api/trades", json={"action": "buy", "ticker": "BCSC", "shares": 10})
    client.post(
        "/api/orders",
        json={"ticker": "BCSC", "kind": "stop_loss", "price": 999999, "shares": 5},
    )
    client.post("/api/game/advance")
    orders = client.get("/api/orders").json()["orders"]
    assert any(
        order["kind"] == "stop_loss" and order["status"] == "filled"
        for order in orders
    )
    assert client.get("/api/replay").json()["stats"]["total_trades"] >= 2


def test_duel_pays_when_player_wins(client):
    from app import models
    from app.database import SessionLocal

    db = SessionLocal()
    player = db.query(models.Player).first()
    player.cash = 1_000_000_000
    rival = db.query(models.Rival).order_by(models.Rival.total_value).first()
    rival_id = rival.id
    db.commit()
    db.close()

    response = client.post(
        "/api/duels",
        json={"rival_id": rival_id, "stake": 500, "days": 1},
    )
    assert response.status_code == 200
    advance = client.post("/api/game/advance").json()
    results = advance["duel_results"]
    assert results and results[0]["result"] == "won"
    assert results[0]["payout"] == 1000
    duels = client.get("/api/duels").json()["duels"]
    assert duels[0]["status"] == "won"


def test_reset_keeps_host_achievements(client):
    response = client.post(
        "/api/trades", json={"action": "buy", "ticker": "GSLX", "shares": 30}
    )
    assert "first_trade" in response.json()["unlocked_achievements"]
    client.post("/api/game/reset")
    achievements = client.get("/api/achievements").json()
    unlocked = {
        achievement["code"]
        for achievement in achievements["achievements"]
        if achievement["unlocked"]
    }
    assert "first_trade" in unlocked
    state = client.get("/api/state").json()
    assert state["portfolio"]["cash"] == 100000
