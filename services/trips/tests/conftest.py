import sqlite3
import pytest
from trips import packs_client

@pytest.fixture
def test_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    with open("database/schema.sql") as f:
        conn.executescript(f.read())

    conn.execute(
        "INSERT INTO locations (city, country, latitude, longitude) VALUES (?, ?, ?, ?)",
        ("Madrid", "Spain", "40.4N", "3.7W"),
    )
    location_id = conn.execute(
        "SELECT id FROM locations WHERE city = ? AND country = ?", ("Madrid", "Spain")
    ).fetchone()["id"]

    conn.execute(
        "INSERT INTO climate_monthly (location_id, month, avg_temp_c, precip_mm) VALUES (?, ?, ?, ?)",
        (location_id, 6, 22.0, 40.0),
    )

    yield conn
    conn.close()
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
def fake_packs(monkeypatch):
    calls = {"replace": [], "delete": [], "up": True}

    def fake_replace(trip_id, items):
        calls["replace"].append((trip_id, items))
        return calls["up"]

    def fake_delete(trip_id):
        calls["delete"].append(trip_id)
        return calls["up"]

    monkeypatch.setattr(packs_client, "replace_recommended", fake_replace)
    monkeypatch.setattr(packs_client, "delete_items", fake_delete)
    return calls