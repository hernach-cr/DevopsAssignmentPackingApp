import sqlite3
import pytest
from packs import trips_client

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    from database import seed
    seed.main()

    from app import app as flask_app
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as test_client:
        yield test_client

@pytest.fixture(autouse=True)
def fake_trips(monkeypatch):
    state = {"answer": True}

    def fake_trip_exists(trip_id):
        return state["answer"]

    monkeypatch.setattr(trips_client, "trip_exists", fake_trip_exists)
    return state