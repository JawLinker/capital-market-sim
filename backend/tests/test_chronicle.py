def test_chronicle_returns_current_arc(client):
    response = client.get("/api/chronicle")
    assert response.status_code == 200
    body = response.json()
    assert body["title"]
    assert body["summary"]
    assert body["current_beat"]
    assert len(body["beats"]) >= 3
    statuses = {beat["status"] for beat in body["beats"]}
    assert statuses <= {"passed", "current", "locked"}
    current = next(beat for beat in body["beats"] if beat["status"] == "current")
    assert current["objective"] is not None
    assert "current" in current["objective"]
    assert "met" in current["objective"]


def test_chronicle_advances_to_next_beat(client):
    before = client.get("/api/chronicle").json()
    client.post("/api/game/advance", json={"days": 70})
    after = client.get("/api/chronicle").json()
    assert after["current_beat"] != before["current_beat"]


def test_chronicle_localization(client):
    en = client.get("/api/chronicle", headers={"accept-language": "en"}).json()
    zh = client.get("/api/chronicle", headers={"accept-language": "zh"}).json()
    assert en["title"] != zh["title"]
    assert en["beats"][0]["title"] != zh["beats"][0]["title"]
