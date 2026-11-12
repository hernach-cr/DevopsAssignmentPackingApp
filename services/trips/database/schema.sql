PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    latitude TEXT,
    longitude TEXT,
    UNIQUE (city, country)
);

CREATE TABLE IF NOT EXISTS climate_monthly (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    avg_temp_c REAL NOT NULL,
    std_temp_c REAL,
    precip_mm REAL,
    FOREIGN KEY (location_id) REFERENCES locations(id),
    UNIQUE (location_id, month)
);

CREATE TABLE IF NOT EXISTS trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    accommodation_type TEXT NOT NULL DEFAULT 'hotel',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);

