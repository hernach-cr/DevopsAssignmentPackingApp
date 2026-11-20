CREATE TABLE locations (
    id INT IDENTITY(1,1) PRIMARY KEY,
    city NVARCHAR(100) NOT NULL,
    country NVARCHAR(100) NOT NULL,
    latitude NVARCHAR(20),
    longitude NVARCHAR(20),
    UNIQUE (city, country)
);

CREATE TABLE climate_monthly (
    id INT IDENTITY(1,1) PRIMARY KEY,
    location_id INT NOT NULL,
    month INT NOT NULL CHECK (month BETWEEN 1 AND 12),
    avg_temp_c FLOAT NOT NULL,
    std_temp_c FLOAT,
    precip_mm FLOAT,
    FOREIGN KEY (location_id) REFERENCES locations(id),
    UNIQUE (location_id, month)
);

CREATE TABLE trips (
    id INT IDENTITY(1,1) PRIMARY KEY,
    location_id INT NOT NULL,
    start_date NVARCHAR(10) NOT NULL,
    end_date NVARCHAR(10) NOT NULL,
    accommodation_type NVARCHAR(50) NOT NULL DEFAULT 'hotel',
    created_at DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
    FOREIGN KEY (location_id) REFERENCES locations(id)
);