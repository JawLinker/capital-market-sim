def test_bots_are_seeded(client):
    data = client.get("/api/bots").json()
    assert len(data["bots"]) == 40
    for bot in data["bots"]:
        assert bot["positions"] > 0
        assert bot["value"] > 0
    assert data["recent_trades"] == []


def test_bots_trade_and_stay_consistent(client):
    for _ in range(5):
        client.post("/api/game/advance")
    data = client.get("/api/bots").json()
    assert data["recent_trades"]
    assert all(trade["action"] in ("buy", "sell") for trade in data["recent_trades"])
    for bot in data["bots"]:
        assert abs(bot["cash"] + bot["invested"] - bot["value"]) < 1.0

    quote = client.get("/api/stocks/BCSC").json()
    assert "bot_net_flow" in quote


def test_bot_flow_impact_is_bounded(client):
    for _ in range(20):
        result = client.post("/api/game/advance").json()["result"]
    assert result["day"] == 20


def test_reset_clears_bot_trades(client):
    for _ in range(3):
        client.post("/api/game/advance")
    assert client.get("/api/bots").json()["recent_trades"]
    client.post("/api/game/reset")
    data = client.get("/api/bots").json()
    assert data["recent_trades"] == []
    assert len(data["bots"]) == 40


def test_bot_history_endpoint(client):
    bot_id = client.get("/api/bots").json()["bots"][0]["id"]
    detail = client.get(f"/api/bots/{bot_id}").json()
    assert len(detail["equity"]) == 1
    assert detail["equity"][0]["day"] == 0
    assert detail["trades"] == []

    for _ in range(3):
        client.post("/api/game/advance")
    detail = client.get(f"/api/bots/{bot_id}").json()
    assert len(detail["equity"]) == 4
    assert detail["equity"][-1]["day"] == 3
    assert detail["value"] == detail["equity"][-1]["value"]

    client.post("/api/game/reset")
    detail = client.get(f"/api/bots/{bot_id}").json()
    assert len(detail["equity"]) == 1
    assert detail["trades"] == []


def test_bot_history_404(client):
    assert client.get("/api/bots/99999").status_code == 404
