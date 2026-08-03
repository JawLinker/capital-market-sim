from collections.abc import Generator

import hashlib
import hmac
import secrets

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import DATABASE_URL


class Base(DeclarativeBase):
    pass


connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def ensure_schema_compat() -> None:
    """Add columns introduced after the first release without dropping data."""
    with engine.begin() as connection:
        additions = {
            "news_events": [
                ("kind", "VARCHAR(32)"),
            ],
            "stocks": [
                ("eps_estimate", "FLOAT DEFAULT 0.1"),
                ("eps_actual", "FLOAT DEFAULT 0.1"),
                ("earnings_growth", "FLOAT DEFAULT 0.08"),
                ("earnings_quality", "FLOAT DEFAULT 0.7"),
                ("style_growth", "FLOAT DEFAULT 0.5"),
                ("last_surprise_pct", "FLOAT DEFAULT 0"),
                ("next_earnings_day", "INTEGER DEFAULT 20"),
                ("prev_daily_ret", "FLOAT DEFAULT 0"),
                ("bid", "FLOAT DEFAULT 0"),
                ("ask", "FLOAT DEFAULT 0"),
                ("bid_depth", "INTEGER DEFAULT 0"),
                ("ask_depth", "INTEGER DEFAULT 0"),
                ("liquidity_factor", "FLOAT DEFAULT 1"),
                ("limit_pct", "FLOAT DEFAULT 10"),
                ("player_impact", "FLOAT DEFAULT 0"),
            ],
            "game_state": [
                ("policy_rate", "FLOAT DEFAULT 4.25"),
                ("inflation", "FLOAT DEFAULT 3.1"),
                ("style_factor", "FLOAT DEFAULT 0"),
                ("next_rate_day", "INTEGER DEFAULT 12"),
                ("regime_count", "INTEGER DEFAULT 0"),
                ("replay_index", "INTEGER DEFAULT 504"),
                ("shanghai_index", "FLOAT DEFAULT 3000"),
                ("shanghai_prev", "FLOAT DEFAULT 3000"),
            ],
            "holdings": [
                ("locked_shares", "FLOAT DEFAULT 0"),
            ],
            "transactions": [
                ("stamp_tax", "FLOAT DEFAULT 0"),
                ("dark_pool", "INTEGER DEFAULT 0"),
            ],
            "players": [
                ("username", "VARCHAR(40) DEFAULT 'host'"),
                ("password_hash", "VARCHAR(128) DEFAULT ''"),
                ("api_key", "VARCHAR(64) DEFAULT ''"),
                ("is_host", "INTEGER DEFAULT 0"),
                ("margin_debt", "FLOAT DEFAULT 0"),
            ],
        }
        for table, columns in additions.items():
            existing = [
                row[1] for row in connection.execute(text(f"PRAGMA table_info({table})"))
            ]
            for column, definition in columns:
                if existing and column not in existing:
                    connection.execute(
                        text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
                    )

        # Upgrade pre-multiplayer saves: the first legacy player becomes the
        # default host account so friends can log in and multiplayer works.
        legacy = connection.execute(
            text(
                "SELECT id FROM players "
                "WHERE password_hash = '' OR password_hash IS NULL "
                "ORDER BY id LIMIT 1"
            )
        ).fetchone()
        if legacy is not None:
            salt = secrets.token_hex(16)
            digest = hashlib.pbkdf2_hmac(
                "sha256", b"123456", bytes.fromhex(salt), 100_000
            ).hex()
            connection.execute(
                text(
                    "UPDATE players SET "
                    "username = 'host', "
                    "password_hash = :hash, "
                    "api_key = :key, "
                    "is_host = 1 "
                    "WHERE id = :id"
                ),
                {
                    "hash": f"{salt}${digest}",
                    "key": secrets.token_urlsafe(24),
                    "id": legacy[0],
                },
            )


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
