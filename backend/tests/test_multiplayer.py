def _register(client, username, password="1234"):
    response = client.post(
        "/api/auth/register",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()["api_key"]


def test_default_host_account_exists(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "host", "password": "123456"},
    )
    assert response.status_code == 200
    player = response.json()
    assert player["is_host"] is True
    assert player["username"] == "host"


def test_second_player_is_guest_and_cannot_advance(client):
    guest_key = _register(client, "guest1")
    response = client.post(
        "/api/game/advance",
        json={"days": 1},
        headers={"X-API-Key": guest_key},
    )
    assert response.status_code == 403

    response = client.post(
        "/api/game/reset",
        headers={"X-API-Key": guest_key},
    )
    assert response.status_code == 403

    response = client.post("/api/game/advance", json={"days": 1})
    assert response.status_code == 200
    assert response.json()["days_advanced"] == 1


def test_leaderboard_contains_all_players(client):
    host_key = client.post(
        "/api/auth/login",
        json={"username": "host", "password": "123456"},
    ).json()["api_key"]
    guest_key = _register(client, "guest2")

    response = client.get(
        "/api/leaderboard",
        headers={"X-API-Key": guest_key},
    )
    assert response.status_code == 200
    data = response.json()
    players = [entry for entry in data["entries"] if entry["kind"] == "player"]
    assert len(players) == 2
    by_name = {entry["name"]: entry for entry in players}
    assert by_name["Host"]["is_current"] is False
    assert by_name["guest2"]["is_current"] is True
    assert data["player_rank"] == by_name["guest2"]["rank"]


def test_guest_portfolio_is_isolated(client):
    guest_key = _register(client, "guest3")
    host_key = client.post(
        "/api/auth/login",
        json={"username": "host", "password": "123456"},
    ).json()["api_key"]

    guest_portfolio = client.get(
        "/api/portfolio",
        headers={"X-API-Key": guest_key},
    ).json()
    host_portfolio = client.get(
        "/api/portfolio",
        headers={"X-API-Key": host_key},
    ).json()
    assert guest_portfolio["summary"]["cash"] == 100_000.0
    assert host_portfolio["summary"]["cash"] == 100_000.0
    assert guest_portfolio["summary"]["value"] == 100_000.0
    assert host_portfolio["summary"]["value"] == 100_000.0


def test_player_activity_shows_other_players(client):
    host_key = client.post(
        "/api/auth/login",
        json={"username": "host", "password": "123456"},
    ).json()["api_key"]
    guest_key = _register(client, "activityguest")

    buy = client.post(
        "/api/trades",
        json={"action": "buy", "ticker": "BCSC", "shares": 5},
        headers={"X-API-Key": host_key},
    )
    assert buy.status_code == 200

    response = client.get(
        "/api/players/activity?limit=20",
        headers={"X-API-Key": guest_key},
    )
    assert response.status_code == 200
    trades = response.json()["trades"]
    host_trade = next(t for t in trades if t["player"] == "host")
    assert host_trade["action"] == "buy"
    assert host_trade["ticker"] == "BCSC"
    assert host_trade["is_current"] is False

    guest_buy = client.post(
        "/api/trades",
        json={"action": "buy", "ticker": "GSLX", "shares": 3},
        headers={"X-API-Key": guest_key},
    )
    assert guest_buy.status_code == 200
    response = client.get(
        "/api/players/activity?limit=20",
        headers={"X-API-Key": guest_key},
    )
    trades = response.json()["trades"]
    guest_trade = next(t for t in trades if t["player"] == "activityguest")
    assert guest_trade["is_current"] is True
