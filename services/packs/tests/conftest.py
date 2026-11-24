import os

import pymssql
import pytest


os.environ["DB_NAME"] = "packs_test"
os.environ["DB_USER"] = "sa"
os.environ["DB_PASSWORD"] = os.environ["MSSQL_SA_PASSWORD"]

from database import migrate 
from packs import trips_client  


@pytest.fixture(scope="session", autouse=True)
def test_database():
    conn = pymssql.connect(
        server=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "1433")),
        user="sa",
        password=os.environ["MSSQL_SA_PASSWORD"],
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