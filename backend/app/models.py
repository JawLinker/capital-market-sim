from datetime import UTC, datetime

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from .database import Base


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(8), unique=True, nullable=False, index=True)
    name = Column(String(80), nullable=False)
    industry = Column(String(24), nullable=False, index=True)
    price = Column(Float, nullable=False)
    prev_close = Column(Float, nullable=False)
    volatility = Column(Float, nullable=False)
    market_cap = Column(Float, nullable=False)
    pe_ratio = Column(Float, nullable=False)
    beta = Column(Float, nullable=False)
    fundamental_price = Column(Float, nullable=False)
    eps_estimate = Column(Float, nullable=False, default=0.1)
    eps_actual = Column(Float, nullable=False, default=0.1)
    earnings_growth = Column(Float, nullable=False, default=0.08)
    earnings_quality = Column(Float, nullable=False, default=0.7)
    style_growth = Column(Float, nullable=False, default=0.5)
    last_surprise_pct = Column(Float, nullable=False, default=0.0)
    next_earnings_day = Column(Integer, nullable=False, default=20)
    prev_daily_ret = Column(Float, nullable=False, default=0.0)
    bid = Column(Float, nullable=False, default=0.0)
    ask = Column(Float, nullable=False, default=0.0)
    bid_depth = Column(Integer, nullable=False, default=0)
    ask_depth = Column(Integer, nullable=False, default=0)
    liquidity_factor = Column(Float, nullable=False, default=1.0)
    limit_pct = Column(Float, nullable=False, default=10.0)
    volume = Column(Integer, nullable=False)
    avg_volume = Column(Integer, nullable=False)
    fifty_two_week_high = Column(Float, nullable=False)
    fifty_two_week_low = Column(Float, nullable=False)
    momentum_20d = Column(Float, default=0.0)
    momentum_60d = Column(Float, default=0.0)
    updated_at = Column(String(32), default=utc_now)


class PriceHistory(Base):
    __tablename__ = "price_history"
    __table_args__ = (UniqueConstraint("stock_id", "trade_date", name="uq_price_date"),)

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    trade_date = Column(String(12), nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)
    username = Column(String(40), nullable=False, default="host")
    password_hash = Column(String(128), nullable=False, default="")
    api_key = Column(String(64), nullable=False, default="")
    is_host = Column(Integer, nullable=False, default=0)
    starting_cash = Column(Float, nullable=False)
    cash = Column(Float, nullable=False)
    created_at = Column(String(32), default=utc_now)


class StorylineProgress(Base):
    __tablename__ = "storyline_progress"
    __table_args__ = (UniqueConstraint("player_id", "npc_key", name="uq_storyline_player"),)

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    npc_key = Column(String(32), nullable=False)
    chapter = Column(Integer, nullable=False, default=0)
    completed_at = Column(String(32), default=utc_now)


class RankStreak(Base):
    __tablename__ = "rank_streaks"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    current_streak = Column(Integer, nullable=False, default=0)
    best_streak = Column(Integer, nullable=False, default=0)
    last_day = Column(Integer, nullable=False, default=-1)


class PendingOrder(Base):
    __tablename__ = "pending_orders"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    kind = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)
    shares = Column(Float, nullable=False)
    created_day = Column(Integer, nullable=False)
    status = Column(String(12), nullable=False, default="open")
    filled_day = Column(Integer, nullable=True)


class Duel(Base):
    __tablename__ = "duels"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    rival_id = Column(Integer, ForeignKey("rivals.id"), nullable=False, index=True)
    stake = Column(Float, nullable=False)
    start_day = Column(Integer, nullable=False)
    end_day = Column(Integer, nullable=False)
    status = Column(String(12), nullable=False, default="open")
    player_return = Column(Float, nullable=True)
    rival_return = Column(Float, nullable=True)
    settled_day = Column(Integer, nullable=True)
    created_at = Column(String(32), default=utc_now)


class Holding(Base):
    __tablename__ = "holdings"
    __table_args__ = (UniqueConstraint("player_id", "stock_id", name="uq_holding"),)

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    shares = Column(Float, nullable=False)
    avg_cost = Column(Float, nullable=False)
    locked_shares = Column(Float, nullable=False, default=0.0)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    action = Column(String(8), nullable=False)
    shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    gross = Column(Float, nullable=False)
    fee = Column(Float, nullable=False)
    stamp_tax = Column(Float, nullable=False, default=0.0)
    net = Column(Float, nullable=False)
    realized_pnl = Column(Float, nullable=False, default=0.0)
    day = Column(Integer, nullable=False)
    executed_at = Column(String(32), default=utc_now)


class NewsEvent(Base):
    __tablename__ = "news_events"

    id = Column(Integer, primary_key=True)
    day = Column(Integer, nullable=False, index=True)
    headline = Column(String(160), nullable=False)
    summary = Column(Text, nullable=False)
    category = Column(String(12), nullable=False)
    scope = Column(String(12), nullable=False)
    kind = Column(String(32), nullable=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=True)
    industry = Column(String(24), nullable=True)
    impact_pct = Column(Float, nullable=False)
    created_at = Column(String(32), default=utc_now)


class EarningsReport(Base):
    __tablename__ = "earnings_reports"

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    day = Column(Integer, nullable=False, index=True)
    eps_estimate = Column(Float, nullable=False)
    eps_actual = Column(Float, nullable=False)
    surprise_pct = Column(Float, nullable=False)
    reaction_pct = Column(Float, nullable=False)
    created_at = Column(String(32), default=utc_now)


class GameState(Base):
    __tablename__ = "game_state"

    id = Column(Integer, primary_key=True)
    day = Column(Integer, nullable=False, default=0)
    date = Column(String(12), nullable=False)
    market_cycle = Column(String(12), nullable=False, default="recovery")
    sentiment = Column(Float, nullable=False, default=1.0)
    regime_strength = Column(Float, nullable=False, default=0.0)
    benchmark_value = Column(Float, nullable=False, default=100.0)
    benchmark_prev = Column(Float, nullable=False, default=100.0)
    next_regime_day = Column(Integer, nullable=False, default=30)
    policy_rate = Column(Float, nullable=False, default=4.25)
    inflation = Column(Float, nullable=False, default=3.1)
    style_factor = Column(Float, nullable=False, default=0.0)
    next_rate_day = Column(Integer, nullable=False, default=12)
    regime_count = Column(Integer, nullable=False, default=0)
    replay_index = Column(Integer, nullable=False, default=504)
    shanghai_index = Column(Float, nullable=False, default=3000.0)
    shanghai_prev = Column(Float, nullable=False, default=3000.0)


class PortfolioHistory(Base):
    __tablename__ = "portfolio_history"
    __table_args__ = (UniqueConstraint("player_id", "day", name="uq_portfolio_day"),)

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    day = Column(Integer, nullable=False)
    date = Column(String(12), nullable=False)
    value = Column(Float, nullable=False)
    cash = Column(Float, nullable=False)
    invested = Column(Float, nullable=False)


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True)
    code = Column(String(40), unique=True, nullable=False)
    title = Column(String(80), nullable=False)
    description = Column(String(240), nullable=False)
    category = Column(String(24), nullable=False)


class UnlockedAchievement(Base):
    __tablename__ = "unlocked_achievements"
    __table_args__ = (
        UniqueConstraint("player_id", "achievement_id", name="uq_unlock"),
    )

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    unlocked_at = Column(String(32), default=utc_now)


class Rival(Base):
    __tablename__ = "rivals"

    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    strategy = Column(String(30), nullable=False)
    cash = Column(Float, nullable=False)
    invested_value = Column(Float, nullable=False)
    total_value = Column(Float, nullable=False)
    weights = Column(Text, nullable=False)  # JSON sector weights


class BotHolding(Base):
    __tablename__ = "bot_holdings"
    __table_args__ = (UniqueConstraint("bot_id", "stock_id", name="uq_bot_holding"),)

    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, ForeignKey("rivals.id"), nullable=False, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    shares = Column(Float, nullable=False)
    avg_cost = Column(Float, nullable=False)


class BotTrade(Base):
    __tablename__ = "bot_trades"

    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, ForeignKey("rivals.id"), nullable=False, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    action = Column(String(8), nullable=False)
    shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    notional = Column(Float, nullable=False)
    day = Column(Integer, nullable=False, index=True)
    created_at = Column(String(32), default=utc_now)


class BotHistory(Base):
    __tablename__ = "bot_history"
    __table_args__ = (UniqueConstraint("bot_id", "day", name="uq_bot_history_day"),)

    id = Column(Integer, primary_key=True)
    bot_id = Column(Integer, ForeignKey("rivals.id"), nullable=False, index=True)
    day = Column(Integer, nullable=False)
    value = Column(Float, nullable=False)
    cash = Column(Float, nullable=False)
    invested = Column(Float, nullable=False)
    created_at = Column(String(32), default=utc_now)
