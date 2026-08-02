def test_initial_state(client):
    response = client.get("/api/state")
    assert response.status_code == 200
    data = response.json()
    assert data["portfolio"]["cash"] == 100000.0
    assert data["portfolio"]["value"] == 100000.0
    assert data["market"]["day"] == 0
    assert data["market"]["shanghai_index"] > 0
    assert data["market"]["market_cycle"] in ("bull", "bear", "recovery", "recession")
    assert len(data["market"]["gainers"]) == 5
    assert len(data["market"]["losers"]) == 5


def test_stock_universe(client):
    response = client.get("/api/stocks")
    assert response.status_code == 200
    stocks = response.json()["stocks"]
    assert len(stocks) == 50
    industries = {stock["industry"] for stock in stocks}
    assert industries == {"technology", "healthcare", "energy", "finance", "consumer"}
    sample = [s for s in stocks if s["ticker"] == "BCSC"][0]
    assert sample["price"] > 0
    assert sample["market_cap"] > 0
    assert sample["pe_ratio"] > 0


def test_stock_history(client):
    response = client.get("/api/stocks/JYZX/history?limit=60")
    assert response.status_code == 200
    series = response.json()["series"]
    assert len(series) == 60
    for point in series:
        assert point["high"] >= point["low"]
        assert point["volume"] > 0


def test_news_feed(client):
    response = client.get("/api/news?limit=10")
    assert response.status_code == 200
    news = response.json()["news"]
    assert len(news) == 0  # no events before the first advance

    client.post("/api/game/advance")
    response = client.get("/api/news?limit=10")
    news = response.json()["news"]
    assert 1 <= len(news) <= 10
    for event in news:
        assert event["category"] in ("positive", "negative", "neutral")
        assert event["scope"] in ("stock", "industry", "market")


def test_shanghai_index_history(client):
    response = client.get("/api/index/history?limit=60")
    assert response.status_code == 200
    data = response.json()
    assert len(data["series"]) == 60
    assert data["name"] == "Shanghai Composite"
    for point in data["series"]:
        assert point["high"] >= point["low"]


def test_fast_forward(client):
    response = client.post("/api/game/advance", json={"days": 30})
    assert response.status_code == 200
    assert response.json()["days_advanced"] == 30
    state = client.get("/api/state").json()
    assert state["market"]["day"] == 30
    performance = client.get("/api/portfolio").json()["performance"]["series"]
    assert len(performance) == 31


def test_fast_forward_rejects_out_of_range(client):
    assert client.post("/api/game/advance", json={"days": 0}).status_code == 422
    assert client.post("/api/game/advance", json={"days": 251}).status_code == 422
