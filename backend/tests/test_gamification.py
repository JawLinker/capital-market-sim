def test_first_trade_achievement(client):
    response = client.post(
        "/api/trades", json={"action": "buy", "ticker": "GSLX", "shares": 30}
    )
    assert "first_trade" in response.json()["unlocked_achievements"]

    achievements = client.get("/api/achievements").json()
    unlocked = [a for a in achievements["achievements"] if a["unlocked"]]
    assert any(a["code"] == "first_trade" for a in unlocked)
    assert len(achievements["milestones"]) == 5


def test_leaderboard_contains_player_and_rivals(client):
    data = client.get("/api/leaderboard").json()
    kinds = {entry["kind"] for entry in data["entries"]}
    assert "player" in kinds
    assert "rival" in kinds
    assert "benchmark" in kinds
    assert data["total_entries"] == 42
    assert 1 <= data["player_rank"] <= 38
