import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _data_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "data"
    return BASE_DIR / "data"


def _frontend_dist_dir() -> Path | None:
    if getattr(sys, "frozen", False):
        meipass = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        bundled = meipass / "frontend_dist"
        return bundled if bundled.exists() else None
    candidate = BASE_DIR.parent / "frontend" / "dist"
    return candidate if candidate.exists() else None


def _snapshot_path() -> Path:
    if getattr(sys, "frozen", False):
        meipass = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        bundled = meipass / "app" / "data" / "a_share_snapshot.json"
        if bundled.exists():
            return bundled
        return meipass / "a_share_snapshot.json"
    return Path(__file__).resolve().parent / "data" / "a_share_snapshot.json"


def _database_url() -> str:
    url = os.environ.get("MARKET_DB_URL")
    if url:
        return url
    data_dir = _data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{data_dir / 'market.db'}"


DATABASE_URL = _database_url()
FRONTEND_DIST = _frontend_dist_dir()
SNAPSHOT_PATH = _snapshot_path()
SEED = int(os.environ.get("MARKET_SEED", "20260801"))
STARTING_CASH = 100_000.0
MIN_ORDER_NOTIONAL = 10.0
FEE_RATE = 0.0015
MIN_FEE = 1.0
HISTORY_DAYS = 504
