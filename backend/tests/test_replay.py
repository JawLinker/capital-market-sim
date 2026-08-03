def test_replay_returns_stats_and_trades(client):
    body = client.get("/api/replay").json()
    assert body["stats"]["total_trades"] >= 0
    assert body["stats"]["win_rate"] >= 0
    assert "max_drawdown" in body["stats"]
    assert "final_return" in body["stats"]
    assert isinstance(body["trades"], list)


def test_replay_tracks_a_trade(client):
    client.post("/api/trades", json={"action": "buy", "ticker": "BCSC", "shares": 10})
    body = client.get("/api/replay").json()
    assert body["stats"]["total_trades"] == 1
    assert body["trades"][0]["ticker"] == "BCSC"
    assert body["trades"][0]["action"] == "buy"
