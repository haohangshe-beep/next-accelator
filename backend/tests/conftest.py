from __future__ import annotations

import os
from pathlib import Path

_DB = Path("/tmp/ftos-acceptance.db")
if _DB.exists():
    _DB.unlink()
os.environ["FTOS_DATABASE_URL"] = f"sqlite:///{_DB}"
os.environ["FTOS_SECRET"] = "test-secret-with-enough-length-32b"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client
