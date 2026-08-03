def test_first_trade_achievement(client):
    response = client.post(
        "/api/trades", json={"action": "buy", "ticker": "GSLX", "shares": 30}
    )
    assert "first_trade" in response.json()["unlocked_achievements"]

    achievements = client.get("/api/achievements").json()
    unlocked = [a for a in achievements["achievements"] if a["unlocked"]]
    assert any(a["code"] == "first_trade" for a in unlocked)
    assert len(achievements["milestones"]) == 5


def test_stock_god_achievement_exists(client):
    achievements = client.get("/api/achievements").json()
    codes = {achievement["code"] for achievement in achievements["achievements"]}
    assert "stock_god" in codes
    assert "three_peat" in codes


def test_consecutive_first_place_unlocks_stock_god(client):
    from app import models
    from app.database import SessionLocal

    db = SessionLocal()
    player = db.query(models.Player).first()
    player.cash = 1_000_000_000
    db.commit()
    db.close()

    for _ in range(5):
        client.post("/api/game/advance")

    achievements = client.get("/api/achievements").json()
    unlocked = {a["code"] for a in achievements["achievements"] if a["unlocked"]}
    assert "three_peat" in unlocked
    assert "stock_god" in unlocked


def test_leaderboard_contains_player_and_rivals(client):
    data = client.get("/api/leaderboard").json()
    kinds = {entry["kind"] for entry in data["entries"]}
    assert "player" in kinds
    assert "rival" in kinds
    assert "benchmark" in kinds
    assert data["total_entries"] == 42
    assert "season" in data
    current = next(entry for entry in data["entries"] if entry.get("is_current"))
    assert "medal" in current
    assert 1 <= data["player_rank"] <= 42
    assert any(entry.get("noodle") for entry in data["entries"])
