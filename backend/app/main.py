from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import FRONTEND_DIST
from .database import Base, SessionLocal, engine, ensure_schema_compat
from .routers import advisor, auth, bots, earnings, gamification, game, news, players, portfolio, stocks, stories, trades
from .seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_schema_compat()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Capital Market Simulator API",
    description="Realistic single-player stock market simulation engine.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game.router)
app.include_router(stocks.router)
app.include_router(earnings.router)
app.include_router(bots.router)
app.include_router(trades.router)
app.include_router(portfolio.router)
app.include_router(players.router)
app.include_router(auth.router)
app.include_router(news.router)
app.include_router(advisor.router)
app.include_router(gamification.router)
app.include_router(stories.router)

@app.get("/health")
def health():
    return {"status": "ok"}


if FRONTEND_DIST is not None:
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
