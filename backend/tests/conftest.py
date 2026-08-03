import os
import tempfile
from pathlib import Path

import pytest

tmp_db = Path(tempfile.gettempdir()) / "capital_market_test.db"
os.environ["MARKET_DB_URL"] = f"sqlite:///{tmp_db}"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.database import Base, engine  # noqa: E402


@pytest.fixture()
def client():
    engine.dispose()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
