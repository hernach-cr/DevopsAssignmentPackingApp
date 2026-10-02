import os
import sqlite3

from flask import Flask, g

from database import seed

app = Flask(__name__)

from trips.routes import trips_bp
app.register_blueprint(trips_bp)

from packs.routes import packing_bp
app.register_blueprint(packing_bp)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(seed.get_db_path())
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/health")
def health():
    db = get_db()
    n = db.execute("SELECT COUNT(*) FROM locations").fetchone()[0]
    return {"status": "ok", "locations_loaded": n}


if __name__ == "__main__":
    seed.main()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)