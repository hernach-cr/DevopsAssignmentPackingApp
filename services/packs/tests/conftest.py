from packs import trips_client
from database import migrate
import os

import pymssql
import pytest

from urllib.parse import quote

SA_PASSWORD = os.environ["MSSQL_SA_PASSWORD"]
DB_HOST = os.environ.get("TEST_DB_HOST", "localhost")
os.environ["DATABASE_URL"] = f"mssql://sa:{quote(SA_PASSWORD, safe='')}@{DB_HOST}:1433/packs_test"


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
    conn.cursor().execute("IF DB_ID('packs_test') IS NULL CREATE DATABASE packs_test")
    conn.close()
    migrate.run()


@pytest.fixture
def client():
    conn = migrate.connect()
    conn.cursor().execute("DELETE FROM packing_items")
    conn.commit()
    conn.close()

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
