import sqlite3
import pytest


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