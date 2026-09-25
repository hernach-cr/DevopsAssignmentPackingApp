import csv
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
CSV_PATH = os.path.join(BASE_DIR, "data", "climate_monthly.csv")


def get_db_path():
    data_dir = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "packing.db")


def create_schema(conn):
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())


def is_already_seeded(conn):
    row = conn.execute("SELECT COUNT(*) FROM climate_monthly").fetchone()
    return row[0] > 0


def seed_climate_data(conn):
    location_ids = {}

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        key = (row["city"], row["country"])
        if key not in location_ids:
            cur = conn.execute(
                "INSERT OR IGNORE INTO locations (city, country, latitude, longitude) "
                "VALUES (?, ?, ?, ?)",
                (row["city"], row["country"], row["latitude"], row["longitude"]),
            )
            loc_id = cur.lastrowid
            if loc_id == 0:
                loc_id = conn.execute(
                    "SELECT id FROM locations WHERE city = ? AND country = ?",
                    key,
                ).fetchone()[0]
            location_ids[key] = loc_id

        precip = row["precip_mm"]
        conn.execute(
            "INSERT INTO climate_monthly "
            "(location_id, month, avg_temp_c, std_temp_c, precip_mm) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                location_ids[key],
                int(row["month"]),
                float(row["avg_temp_c"]),
                float(row["std_temp_c"]) if row["std_temp_c"] else None,
                float(precip) if precip not in ("", None) else None,
            ),
        )

    conn.commit()
    return len(location_ids), len(rows)


def main():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    create_schema(conn)

    if is_already_seeded(conn):
        print(f"Database already seeded at {db_path}, skipping.")
    else:
        n_locations, n_rows = seed_climate_data(conn)
        print(f"Seeded {n_locations} locations and {n_rows} climate_monthly rows into {db_path}")

    conn.close()


if __name__ == "__main__":
    main()