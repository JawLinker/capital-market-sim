def test_advisor_report_empty(client):
    response = client.get("/api/advisor/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["health_score"] <= 100
    assert set(data["dimensions"]) == {"valuation", "momentum", "risk", "diversification"}
    assert data["holdings"] == []


def test_advisor_report_with_holdings(client):
    assert client.post("/api/trades", json={"action": "buy", "ticker": "JCYH", "shares": 5}).status_code == 200
    assert client.post("/api/trades", json={"action": "buy", "ticker": "ZYKY", "shares": 10}).status_code == 200
    data = client.get("/api/advisor/portfolio").json()
    assert len(data["holdings"]) == 2
    for holding in data["holdings"]:
        assert 0 <= holding["composite_score"] <= 100
        for dimension in ("valuation", "momentum", "risk"):
            assert 0 <= holding["dimensions"][dimension]["score"] <= 100
    assert data["allocation"]["total_invested"] > 0


def test_advisor_chat(client):
    client.post("/api/trades", json={"action": "buy", "ticker": "DJDL", "shares": 300})
    response = client.post(
        "/api/advisor/chat",
        json={"message": "How risky is DJDL and should I buy more?"},
    )
    assert response.status_code == 200
    reply = response.json()["reply"]
    assert "China Yangtze Power" in reply
    assert "risk" in reply.lower()
