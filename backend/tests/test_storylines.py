def test_storylines_have_four_npc_chains(client):
    body = client.get("/api/storylines").json()
    assert len(body["storylines"]) == 4
    for storyline in body["storylines"]:
        assert storyline["name"]
        assert storyline["icon"]
        assert len(storyline["chapters"]) == 5
        statuses = {chapter["status"] for chapter in storyline["chapters"]}
        assert statuses <= {"passed", "current", "locked"}
        current = next(
            (chapter for chapter in storyline["chapters"] if chapter["status"] == "current"),
            None,
        )
        if current:
            assert current["objective"] is not None
            assert current["reward"]


def test_storylines_localization(client):
    en = client.get("/api/storylines", headers={"accept-language": "en"}).json()
    zh = client.get("/api/storylines", headers={"accept-language": "zh"}).json()
    assert en["storylines"][0]["name"] != zh["storylines"][0]["name"]
