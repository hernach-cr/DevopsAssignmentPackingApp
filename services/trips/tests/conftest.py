from trips import packs_client
from database import migrate, seed
from app import Db
import os

import pymssql
import pytest
from urllib.parse import quote

SA_PASSWORD = os.environ["MSSQL_SA_PASSWORD"]
DB_HOST = os.environ.get("TEST_DB_HOST", "localhost")
os.environ["DATABASE_URL"] = f"mssql://sa:{quote(SA_PASSWORD, safe='')}@{DB_HOST}:1433/trips_test"


@pytest.fixture(scope="session", autouse=True)
def test_database():
    conn = pymssql.connect(
        server=DB_HOST,
        port=1433,
        user="sa",
        password=SA_PASSWORD,
        database="master",
        autocommit=True,
    )
    conn.cursor().execute("IF DB_ID('trips_test') IS NULL CREATE DATABASE trips_test")
    conn.close()

    migrate.run()
    seed.main()

    # Fix Madrid's June to the values the tests were written for
    conn = migrate.connect()
    conn.cursor().execute(
        "UPDATE climate_monthly SET avg_temp_c = 22.0, std_temp_c = NULL, precip_mm = 40.0 "
        "WHERE month = 6 AND location_id = "
        "(SELECT id FROM locations WHERE city = 'Madrid' AND country = 'Spain')"
    )
    conn.commit()
    conn.close()


@pytest.fixture
def test_db():
    db = Db(migrate.connect())
    yield db
    db.close()


@pytest.fixture
def client():
    conn = migrate.connect()
    conn.cursor().execute("DELETE FROM trips")
    conn.commit()
    conn.close()

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
