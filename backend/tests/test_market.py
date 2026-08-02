def test_advance_updates_state_and_history(client):
    before = client.get("/api/state").json()
    response = client.post("/api/game/advance")
    assert response.status_code == 200
    result = response.json()["result"]
    assert result["day"] == before["market"]["day"] + 1
    assert result["benchmark_value"] > 0

    history = client.get("/api/stocks/BCSC/history?limit=30").json()["series"]
    from app.config import HISTORY_DAYS
    from app.services.replay import replay_rows

    assert history[-1]["date"] == replay_rows()["BCSC"][HISTORY_DAYS]["d"]


def test_advance_snapshots_portfolio(client):
    client.post("/api/trades", json={"action": "buy", "ticker": "GSLX", "shares": 50})
    for _ in range(3):
        client.post("/api/game/advance")
    performance = client.get("/api/portfolio").json()["performance"]["series"]
    assert len(performance) == 4
    assert performance[-1]["day"] == 3
    assert performance[-1]["value"] > 0


def test_advance_past_short_replay_series(client):
    from app import models
    from app.database import SessionLocal
    from app.services.replay import replay_rows

    lengths = {ticker: len(rows) for ticker, rows in replay_rows().items()}
    shortest = min(lengths.values())
    db = SessionLocal()
    state = db.query(models.GameState).first()
    state.replay_index = shortest
    db.commit()
    db.close()

    for _ in range(2):
        response = client.post("/api/game/advance", json={"days": 1})
        assert response.status_code == 200


def test_reset_restores_clean_state(client):
    client.post("/api/trades", json={"action": "buy", "ticker": "BCSC", "shares": 25})
    client.post("/api/game/advance")
    response = client.post("/api/game/reset")
    assert response.status_code == 200
    state = client.get("/api/state").json()
    assert state["market"]["day"] == 0
    assert state["portfolio"]["cash"] == 100000.0
    assert state["portfolio"]["value"] == 100000.0
    assert client.get("/api/transactions").json()["transactions"] == []
