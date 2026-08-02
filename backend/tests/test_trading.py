def test_buy_then_sell(client):
    quote = client.get("/api/stocks/BCSC").json()
    price = quote["price"]
    shares = 100

    buy = client.post(
        "/api/trades", json={"action": "buy", "ticker": "BCSC", "shares": shares}
    )
    assert buy.status_code == 200
    trade = buy.json()["trade"]
    assert trade["shares"] == 100
    assert trade["fee"] >= 1.0
    assert buy.json()["portfolio"]["cash"] < 100000.0
    assert trade["action"] == "buy"

    client.post("/api/game/advance")

    sell = client.post(
        "/api/trades", json={"action": "sell", "ticker": "BCSC", "shares": 40}
    )
    assert sell.status_code == 200
    assert sell.json()["trade"]["action"] == "sell"

    portfolio = client.get("/api/portfolio").json()
    holding = [h for h in portfolio["holdings"] if h["ticker"] == "BCSC"][0]
    assert holding["shares"] == 60.0
    assert holding["market_value"] > 0


def test_rejects_overselling(client):
    client.post("/api/trades", json={"action": "buy", "ticker": "BCSC", "shares": 10})
    client.post("/api/game/advance")
    response = client.post(
        "/api/trades", json={"action": "sell", "ticker": "BCSC", "shares": 11}
    )
    assert response.status_code == 400


def test_oversized_buy_clamps_to_cash(client):
    response = client.post(
        "/api/trades", json={"action": "buy", "ticker": "BCSC", "shares": 100000}
    )
    assert response.status_code == 200
    trade = response.json()["trade"]
    assert trade["shares"] < 100000
    assert trade["shares"] > 0
    assert trade["gross"] + trade["fee"] <= 100000.0 + 0.02
    assert response.json()["portfolio"]["cash"] >= 0.0

    portfolio = client.get("/api/portfolio").json()
    holding = [h for h in portfolio["holdings"] if h["ticker"] == "BCSC"][0]
    assert holding["shares"] == trade["shares"]


def test_minimum_order_size(client):
    quote = client.get("/api/stocks/DLYP").json()
    shares = round(9.0 / quote["ask"], 6)
    response = client.post(
        "/api/trades", json={"action": "buy", "ticker": "DLYP", "shares": shares}
    )
    assert response.status_code == 400
    assert "Minimum order" in response.json()["detail"]


def test_transaction_history(client):
    client.post("/api/trades", json={"action": "buy", "ticker": "GSLX", "shares": 20})
    response = client.get("/api/transactions")
    transactions = response.json()["transactions"]
    assert len(transactions) == 1
    assert transactions[0]["ticker"] == "GSLX"
    assert transactions[0]["day"] == 0
