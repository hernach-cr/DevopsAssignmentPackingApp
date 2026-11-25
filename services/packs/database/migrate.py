import os
import time
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pymssql

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"

def connection_settings():
    url = urlsplit(os.environ["DATABASE_URL"])
    return {
        "server": url.hostname,
        "port": url.port or 1433,
        "user": unquote(url.username),
        "password": unquote(url.password),
        "database": url.path.lstrip("/"),
    }


def connect(retries=10, wait_seconds=3):
    for attempt in range(1, retries + 1):
        try:
            return pymssql.connect(**connection_settings())
        except pymssql.OperationalError:
            if attempt == retries:
                raise
            print(f"Database not ready (attempt {attempt}/{retries}), retrying in {wait_seconds}s")
            time.sleep(wait_seconds)

def run():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "IF OBJECT_ID('schema_migrations') IS NULL "
        "CREATE TABLE schema_migrations ("
        " version NVARCHAR(100) PRIMARY KEY,"
        " applied_at DATETIME2 NOT NULL DEFAULT SYSDATETIME())"
    )
    conn.commit()

    cursor.execute("SELECT version FROM schema_migrations")
    applied = {row[0] for row in cursor.fetchall()}

    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        if path.name in applied:
            continue
        print(f"Applying migration {path.name}")
        sql = path.read_text(encoding="utf-8")
        for statement in sql.split(";"):
            if statement.strip():
                cursor.execute(statement)
        cursor.execute("INSERT INTO schema_migrations (version) VALUES (%s)", (path.name,))
        conn.commit()

    conn.close()