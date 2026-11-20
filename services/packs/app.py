import os
from flask import Flask, g
from database import migrate


app = Flask(__name__)

from flask_cors import CORS
CORS(app, origins=[os.environ.get("UI_ORIGIN", "http://localhost:5500")])

from packs.routes import packing_bp
app.register_blueprint(packing_bp)

class Db:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, sql, params=None):
        cursor = self.conn.cursor(as_dict=True)
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


def get_db():
    if "db" not in g:
        conn = migrate.connect()
        g.db = Db(conn)
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/health")
def health():
    version = os.environ.get("GIT_SHA", "dev")
    try:
        get_db().execute("SELECT 1 AS ok").fetchone()
        return {"status": "ok", "db": "ok", "version": version}
    except Exception:
        return {"status": "error", "db": "unreachable", "version": version}, 503


if __name__ == "__main__":
    migrate.run()
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port)