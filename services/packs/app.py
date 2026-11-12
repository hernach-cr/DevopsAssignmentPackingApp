import os
import sqlite3

from flask import Flask, g

from database import seed


app = Flask(__name__)




from packs.routes import packing_bp
app.register_blueprint(packing_bp)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(seed.get_db_path())
        g.db.row_factory = sqlite3.Row

    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()



@app.route("/health")
def health():
    db = get_db()
    n = db.execute("SELECT COUNT(*) FROM packing_items").fetchone()[0]
    return {"status": "ok", "items": n}


if __name__ == "__main__":
    seed.main()
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)