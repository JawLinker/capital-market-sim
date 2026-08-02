def test_today_story_is_deterministic(client):
    first = client.get("/api/stories/today")
    second = client.get("/api/stories/today")
    assert first.status_code == 200
    assert first.json() == second.json()
    body = first.json()
    assert body["id"].startswith("s")
    assert body["tag"]
    assert body["title"]
    assert body["story"]


def test_random_story_is_valid(client):
    response = client.get("/api/stories/random")
    assert response.status_code == 200
    assert response.json()["id"].startswith("s")


def test_story_follows_game_day(client):
    before = client.get("/api/stories/today").json()
    client.post("/api/game/advance", json={"days": 1})
    after = client.get("/api/stories/today").json()
    assert after["day"] == before["day"] + 1


def test_story_localization(client):
    en = client.get("/api/stories/random", headers={"accept-language": "en"}).json()
    zh = client.get("/api/stories/random", headers={"accept-language": "zh"}).json()
    assert en["title"] != zh["title"] or en["story"] != zh["story"]
