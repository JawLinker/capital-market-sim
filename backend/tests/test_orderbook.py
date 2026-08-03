from app import models
from app.services.orderbook import estimate_market_order, execute_market_order


def _stock(price=100.0):
    stock = models.Stock()
    stock.price = price
    stock.avg_volume = 1_000_000
    stock.volatility = 0.02
    stock.bid = 99.95
    stock.ask = 100.05
    stock.bid_depth = 4000
    stock.ask_depth = 4000
    stock.liquidity_factor = 1.0
    return stock


def _state():
    state = models.GameState()
    state.sentiment = 1.0
    state.market_cycle = "bull"
    return state


def test_small_order_fills_inside_depth():
    stock = _stock()
    state = _state()
    fill = execute_market_order(None, stock, state, 1000, "buy")
    assert fill == stock.ask
    assert stock.price == 100.0
    assert stock.ask_depth == 3000


def test_large_order_walks_the_book():
    stock = _stock()
    state = _state()
    old_ask = stock.ask
    fill = execute_market_order(None, stock, state, 10000, "buy")
    assert fill > old_ask
    assert stock.price > 100.0
    assert stock.ask_depth < 4000


def test_large_sell_walks_price_down():
    stock = _stock()
    state = _state()
    old_bid = stock.bid
    fill = execute_market_order(None, stock, state, 10000, "sell")
    assert fill < old_bid
    assert stock.price < 100.0


def test_estimate_matches_execution():
    stock = _stock()
    state = _state()
    old_ask = stock.ask
    expected = estimate_market_order(stock, state, 10000, "buy")
    fill = execute_market_order(None, stock, state, 10000, "buy")
    assert fill == expected
    assert fill > old_ask


def test_api_trade_uses_book(client):
    quote = client.get("/api/stocks/BCSC").json()
    price = quote["price"]
    ask = quote["ask"]
    depth = quote["ask_depth"]
    shares = min(500, depth - 100)
    assert shares > 0
    trade = client.post(
        "/api/trades",
        json={"action": "buy", "ticker": "BCSC", "shares": shares},
    ).json()["trade"]
    assert trade["price"] == ask
    after = client.get("/api/stocks/BCSC").json()
    assert after["price"] >= price
    assert after["ask_depth"] < depth
