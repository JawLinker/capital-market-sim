"""Real A-share daily replay data loaded from the bundled snapshot."""

import json

from ..config import HISTORY_DAYS, SNAPSHOT_PATH

_CACHE: dict[str, list[dict]] | None = None
_INDEX_CACHE: list[dict] | None = None


def _load() -> dict[str, list[dict]]:
    global _CACHE
    if _CACHE is None:
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        _CACHE = {stock["ticker"]: stock["series"] for stock in snapshot["stocks"]}
    return _CACHE


def replay_rows() -> dict[str, list[dict]]:
    return _load()


def replay_row(ticker: str, index: int) -> dict:
    rows = _load()[ticker]
    return rows[min(index, len(rows) - 1)]


def replay_max_index() -> int:
    return max(len(rows) for rows in _load().values()) - 1


def next_replay_index(current: int) -> int:
    maximum = replay_max_index()
    if current + 1 > maximum:
        return HISTORY_DAYS
    return current + 1


def index_series() -> list[dict]:
    global _INDEX_CACHE
    if _INDEX_CACHE is None:
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        _INDEX_CACHE = snapshot["meta"].get("index_series") or []
    return _INDEX_CACHE


def index_row(index: int) -> dict:
    rows = index_series()
    return rows[min(index, len(rows) - 1)] if rows else {"c": 0.0, "o": 0.0, "h": 0.0, "l": 0.0, "v": 0}
