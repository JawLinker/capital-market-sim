def test_daily_challenge_is_deterministic(client):
    first = client.get("/api/quests/daily").json()
    second = client.get("/api/quests/daily").json()
    assert first == second
    assert first["kind"] == "daily"
    assert first["objective"]["current"] is not None
    assert first["objective"]["met"] in (True, False)
    assert first["reward"]["label"]


def test_commission_has_npc_and_objective(client):
    body = client.get("/api/quests/commission").json()
    assert body["kind"] == "commission"
    assert body["npc"]["name"]
    assert body["npc"]["icon"]
    assert body["description"]
    assert body["objective"]["label"]
    assert body["reward"]["label"]


def test_quests_localization(client):
    en = client.get("/api/quests/daily", headers={"accept-language": "en"}).json()
    zh = client.get("/api/quests/daily", headers={"accept-language": "zh"}).json()
    assert en["title"] != zh["title"]


def test_quest_objectives_are_diverse(client):
    from app.services.chronicle import ARCS
    from app.services.quests import DAILY_POOL
    from app.services.storylines import STORYLINES

    types = []
    for arc in ARCS:
        types += [beat["objective"]["type"] for beat in arc["beats"]]
    types += [task["type"] for task in DAILY_POOL]
    types += [
        chapter["objective"]["type"]
        for storyline in STORYLINES
        for chapter in storyline["chapters"]
    ]
    assert len(set(types)) >= 8
    tech = sum(
        1
        for kind in types
        if kind in {"tech_exposure", "tech_return", "tech_holdings"}
    )
    assert tech / len(types) < 0.4


def test_new_objective_types_evaluate(client):
    from app import models
    from app.database import SessionLocal
    from app.services.chronicle import evaluate_objective

    db = SessionLocal()
    player = db.query(models.Player).first()
    objectives = [
        {"type": "sector_exposure", "industry": "energy", "target": 10, "label_zh": "x", "label_en": "x"},
        {"type": "sector_return", "industry": "energy", "target": 100, "label_zh": "x", "label_en": "x"},
        {"type": "trade_count", "target": 1, "label_zh": "x", "label_en": "x"},
        {"type": "hold_count", "target": 1, "label_zh": "x", "label_en": "x"},
        {"type": "diversified", "target": 1, "label_zh": "x", "label_en": "x"},
        {"type": "daily_gain", "target": 1, "label_zh": "x", "label_en": "x"},
    ]
    for objective in objectives:
        result = evaluate_objective(db, player, objective, "en")
        assert "current" in result
        assert "met" in result
    db.close()


def test_commission_decision_accept(client):
    card = client.get("/api/quests/commission").json()
    assert card["status"] == "open"
    assert card["decision_id"]
    assert {option["key"] for option in card["options"]} == {
        "accept",
        "bargain",
        "reject",
    }
    response = client.post(
        f"/api/quests/commission/{card['decision_id']}/resolve",
        json={"option_key": "accept"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    next_card = client.get("/api/quests/commission").json()
    assert next_card["status"] == "accepted"


def test_commission_bargain_changes_target(client):
    card = client.get("/api/quests/commission").json()
    original = card["objective"]["target"]
    response = client.post(
        f"/api/quests/commission/{card['decision_id']}/resolve",
        json={"option_key": "bargain"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    next_card = client.get("/api/quests/commission").json()
    assert next_card["objective"]["target"] != original


def test_commission_reject_adds_cooldown(client):
    card = client.get("/api/quests/commission").json()
    response = client.post(
        f"/api/quests/commission/{card['decision_id']}/resolve",
        json={"option_key": "reject"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    assert response.json()["cooldown_days"] == 5
    next_card = client.get("/api/quests/commission").json()
    assert next_card["status"] == "rejected"
    assert next_card["cooldown_days"] == 5
