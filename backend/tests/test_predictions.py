def test_create_and_list_judgment(client):
    response = client.post(
        "/api/judgments",
        json={"ticker": "BCSC", "thesis": "rally"},
    )
    assert response.status_code == 200
    data = client.get("/api/judgments").json()
    assert data["judgments"][0]["thesis"] == "rally"
    assert data["judgments"][0]["status"] == "open"


def test_judgment_duplicate_rejected(client):
    payload = {"ticker": "BCSC", "thesis": "dip"}
    assert client.post("/api/judgments", json=payload).status_code == 200
    assert client.post("/api/judgments", json=payload).status_code == 400


def test_validate_judgment_right_and_streak(client):
    from app import models
    from app.database import SessionLocal
    from app.services.predictions import create_judgment, validate_judgments

    db = SessionLocal()
    player = db.query(models.Player).first()
    stock = db.query(models.Stock).first()
    create_judgment(db, player, stock, "rally", 0)
    stock.price = round(stock.price * 1.02, 2)
    db.commit()
    db.close()

    results = validate_judgments(SessionLocal())
    assert results and results[0]["status"] == "right"

    db = SessionLocal()
    prediction = db.query(models.PredictionStreak).first()
    assert prediction is not None
    assert prediction.best_streak == 1
    db.close()


def test_seer_achievements_in_catalog(client):
    achievements = client.get("/api/achievements").json()
    codes = {achievement["code"] for achievement in achievements["achievements"]}
    assert "seer_3" in codes
    assert "seer_5" in codes
