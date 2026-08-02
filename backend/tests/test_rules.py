def test_t_plus_one_blocks_same_day_sell(client):
    buy = client.post(
        "/api/trades", json={"action": "buy", "ticker": "BCSC", "shares": 10}
    )
    assert buy.status_code == 200
    blocked = client.post(
        "/api/trades", json={"action": "sell", "ticker": "BCSC", "shares": 5}
    )
    assert blocked.status_code == 400
    assert "T+1" in blocked.json()["detail"]

    client.post("/api/game/advance")
    ok = client.post(
        "/api/trades", json={"action": "sell", "ticker": "BCSC", "shares": 5}
    )
    assert ok.status_code == 200


def test_stamp_tax_charged_on_sell(client):
    client.post("/api/trades", json={"action": "buy", "ticker": "BCSC", "shares": 10})
    client.post("/api/game/advance")
    sell = client.post(
        "/api/trades", json={"action": "sell", "ticker": "BCSC", "shares": 10}
    ).json()["trade"]
    assert sell["stamp_tax"] > 0
    transactions = client.get("/api/transactions").json()["transactions"]
    assert transactions[0]["stamp_tax"] == sell["stamp_tax"]


def test_limit_up_blocks_buying():
    from app import models
    from app.services.orderbook import execute_market_order, is_limit_up

    stock = models.Stock()
    stock.price = 110.0
    stock.prev_close = 100.0
    stock.limit_pct = 10.0
    stock.bid = 109.5
    stock.ask = 110.0
    stock.bid_depth = 4000
    stock.ask_depth = 0
    stock.liquidity_factor = 1.0
    state = models.GameState()
    state.sentiment = 1.0
    state.market_cycle = "bull"
    assert is_limit_up(stock)
    assert execute_market_order(None, stock, state, 100, "buy") is None
    assert execute_market_order(None, stock, state, 100, "sell") is not None
