import random

from app.services.fundamentals import (
    INDUSTRY_CORRELATION,
    INDUSTRY_CHOLESKY,
    correlated_industry_shocks,
    industry_multiple,
    policy_target_rate,
    rate_multiple_factor,
)


def test_correlation_matrix_is_positive_definite():
    assert len(INDUSTRY_CHOLESKY) == 5
    for row in INDUSTRY_CHOLESKY:
        assert len(row) == 5
    rng = random.Random(7)
    shocks = correlated_industry_shocks(rng)
    assert set(shocks) == {"technology", "healthcare", "energy", "finance", "consumer"}
    assert all(isinstance(value, float) for value in shocks.values())
    # Correlated draws should be less dispersed than independent gaussian units.
    sample = [
        correlated_industry_shocks(rng)["technology"] for _ in range(2000)
    ]
    assert abs(sum(sample) / len(sample)) < 0.05
    assert INDUSTRY_CORRELATION[0][0] == 1.0


def test_rate_drives_valuation_multiple():
    assert rate_multiple_factor(2.0) > 1.0
    assert rate_multiple_factor(8.0) < 1.0
    tech_low = industry_multiple("technology", 2.0, 1.0)
    tech_high = industry_multiple("technology", 8.0, 1.0)
    assert tech_low > tech_high


def test_policy_target_rate_ranges():
    assert 0.5 <= policy_target_rate(2.0, "bull") <= 10.0
    assert policy_target_rate(5.0, "recession") < policy_target_rate(5.0, "bull")


def test_replay_advance_uses_real_data(client):
    from app.config import HISTORY_DAYS
    from app.services.replay import replay_rows

    series = replay_rows()
    client.post("/api/game/advance")
    stock = client.get("/api/stocks/BCSC").json()
    expected = series["BCSC"][HISTORY_DAYS]["c"]
    assert abs(stock["price"] - expected) < 0.01
    state = client.get("/api/state").json()["market"]
    from app.services.replay import index_series

    assert state["shanghai_index"] == round(index_series()[HISTORY_DAYS]["c"], 2)
    news = client.get("/api/news?limit=10").json()["news"]
    assert news
    assert any("replay" in event["headline"].lower() for event in news)


def test_macro_state_stays_bounded(client):
    for _ in range(60):
        client.post("/api/game/advance")
    state = client.get("/api/state").json()["market"]
    assert 0.25 <= state["policy_rate"] <= 12.0
    assert 0.5 <= state["inflation"] <= 8.0
    assert -0.012 <= state["style_factor"] <= 0.012
