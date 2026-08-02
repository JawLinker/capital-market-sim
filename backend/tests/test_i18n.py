ZH = {"Accept-Language": "zh-CN"}


def test_chinese_stock_names(client):
    response = client.get("/api/stocks", headers=ZH)
    stocks = response.json()["stocks"]
    assert stocks[0]["ticker"] == "BCSC"
    assert stocks[0]["name"] == "\u767e\u6d4e\u795e\u5dde"

    english = client.get("/api/stocks").json()["stocks"][0]
    assert english["name"] == "BeiGene"


def test_chinese_news(client):
    client.post("/api/game/advance")
    response = client.get("/api/news", headers=ZH)
    assert response.status_code == 200
    news = response.json()["news"]
    assert news
    assert any(
        any("\u4e00" <= char <= "\u9fff" for char in event["headline"])
        for event in news
    )


def test_chinese_achievements(client):
    client.post("/api/trades", json={"action": "buy", "ticker": "GSLX", "shares": 30})
    achievements = client.get("/api/achievements", headers=ZH).json()["achievements"]
    first = next(a for a in achievements if a["code"] == "first_trade")
    assert first["title"] == "\u7b2c\u4e00\u7b14\u4ea4\u6613"


def test_chinese_advisor(client):
    client.post("/api/trades", json={"action": "buy", "ticker": "DJDL", "shares": 50})
    report = client.get("/api/advisor/portfolio", headers=ZH).json()
    assert report["education"][0].startswith("\u4f30\u503c")

    message = "\u6211\u7684\u5206\u6563\u5316\u5982\u4f55\uff1f"
    reply = client.post(
        "/api/advisor/chat", headers=ZH, json={"message": message}
    ).json()["reply"]
    assert "\u5206\u6563\u5316\u5f97\u5206" in reply
