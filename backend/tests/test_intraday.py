def test_intraday_endpoint_returns_live_price(client):
    quote = client.get("/api/stocks/BCSC").json()
    data = client.get(
        "/api/stocks/BCSC/intraday",
        params={"elapsed": 45, "window": 120},
    ).json()
    assert data["base"] == quote["price"]
    assert data["price"] > 0
    band = quote["limit_pct"] / 100.0
    assert quote["prev_close"] * (1 - band) <= data["price"] <= quote["prev_close"] * (1 + band)


def test_intraday_trade_fills_at_live_price(client):
    quote = client.get("/api/stocks/BCSC").json()
    live = round(quote["price"] * 1.01, 2)
    trade = client.post(
        "/api/trades",
        json={
            "action": "buy",
            "ticker": "BCSC",
            "shares": 10,
            "intraday_price": live,
        },
    ).json()["trade"]
    assert trade["price"] == live
