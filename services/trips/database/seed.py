import csv
import os

from database import migrate

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "climate_monthly.csv")


def is_already_seeded(cursor):
    cursor.execute("SELECT COUNT(*) FROM climate_monthly")
    return cursor.fetchone()[0] > 0


def seed_climate_data(conn):
    cursor = conn.cursor()
    location_ids = {}

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        key = (row["city"], row["country"])
        if key not in location_ids:
            cursor.execute(
                "INSERT INTO locations (city, country, latitude, longitude) "
                "VALUES (%s, %s, %s, %s)",
                (row["city"], row["country"], row["latitude"], row["longitude"]),
            )
            location_ids[key] = int(cursor.lastrowid)

        precip = row["precip_mm"]
        cursor.execute(
            "INSERT INTO climate_monthly "
            "(location_id, month, avg_temp_c, std_temp_c, precip_mm) "
            "VALUES (%s, %s, %s, %s, %s)",
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
    conn = migrate.connect()
    cursor = conn.cursor()
    if is_already_seeded(cursor):
        print("Climate data already loaded, skipping.")
    else:
        n_locations, n_rows = seed_climate_data(conn)
        print(f"Seeded {n_locations} locations and {n_rows} climate rows")
    conn.close()