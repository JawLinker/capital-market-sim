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
