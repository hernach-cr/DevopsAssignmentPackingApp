
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")



def get_db_path():
    data_dir = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "packing.db")


def create_schema(conn):
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())




def main():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    create_schema(conn)

   

    conn.close()


if __name__ == "__main__":
    main()