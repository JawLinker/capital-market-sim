import random

from app.services.blackswan import BLACK_SWANS, eligible_black_swans, pick_black_swan


def test_black_swan_pool_has_era_events():
    june_2026 = eligible_black_swans("2026-06-15")
    assert any(event["id"] == "bs09" for event in june_2026)
    outside = eligible_black_swans("2021-02-01")
    assert all(event["from_date"] > "2021-02-01" for event in outside)
    all_ids = {event["id"] for event in BLACK_SWANS}
    assert {"bs11", "bs12", "bs13", "bs14", "bs15", "bs16", "bs17"} <= all_ids
    assert {event["id"] for event in eligible_black_swans("2026-05-01")} == {"bs17"}


def test_black_swan_pick_is_deterministic_with_seed():
    first = pick_black_swan("2026-06-15", random.Random(7))
    second = pick_black_swan("2026-06-15", random.Random(7))
    assert first["id"] == second["id"]


def test_advance_response_includes_black_swan_key(client):
    response = client.post("/api/game/advance", json={"days": 1})
    assert response.status_code == 200
    body = response.json()
    assert "black_swan" in body
    assert body["black_swan"] is None or body["black_swan"]["title"]
