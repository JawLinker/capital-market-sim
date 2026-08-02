def test_legends_are_anonymized(client):
    response = client.get("/api/legends")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] >= 8
    for legend in body["legends"]:
        assert legend["file_no"].startswith("LG-")
        assert legend["title"]
        assert legend["story"]
        assert legend["footnote"]


def test_timeline_is_factual(client):
    response = client.get("/api/timeline")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] >= 10
    years = [event["year"] for event in body["events"]]
    assert years == sorted(years)
    assert all(event["title"] and event["fact"] for event in body["events"])


def test_legends_localization(client):
    en = client.get("/api/legends", headers={"accept-language": "en"}).json()["legends"][0]
    zh = client.get("/api/legends", headers={"accept-language": "zh"}).json()["legends"][0]
    assert en["title"] != zh["title"]
    assert en["footnote"] != zh["footnote"]
