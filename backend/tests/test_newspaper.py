def test_newspaper_collects_giant_earnings(client):
    from app import models
    from app.database import SessionLocal
    from app.services.newspaper import collect_newspaper

    db = SessionLocal()
    stocks = db.query(models.Stock).order_by(models.Stock.market_cap.desc()).all()
    giant = stocks[0]
    db.add(
        models.NewsEvent(
            day=0,
            headline="placeholder",
            summary="placeholder",
            category="stock",
            scope="stock",
            kind="earnings_beat",
            stock_id=giant.id,
            impact_pct=3.2,
        )
    )
    db.commit()
    db.close()

    items = collect_newspaper(SessionLocal(), 0, "en")
    assert items
    assert items[0]["ticker"] == giant.ticker
    assert items[0]["kind"] == "earnings_beat"
    assert "crushes" in items[0]["headline"]


def test_newspaper_ignores_small_company(client):
    from app import models
    from app.database import SessionLocal
    from app.services.newspaper import collect_newspaper

    db = SessionLocal()
    stocks = db.query(models.Stock).order_by(models.Stock.market_cap.asc()).all()
    small = stocks[0]
    db.add(
        models.NewsEvent(
            day=0,
            headline="placeholder",
            summary="placeholder",
            category="stock",
            scope="stock",
            kind="earnings_beat",
            stock_id=small.id,
            impact_pct=3.2,
        )
    )
    db.commit()
    db.close()
    assert collect_newspaper(SessionLocal(), 0, "en") == []
