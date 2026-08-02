import os
import tempfile
from pathlib import Path

import pytest

tmp_db = Path(tempfile.gettempdir()) / "capital_market_test.db"
if tmp_db.exists():
    tmp_db.unlink()
os.environ["MARKET_DB_URL"] = f"sqlite:///{tmp_db}"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        test_client.post("/api/game/reset")
        yield test_client
