from datetime import datetime

from flask import Blueprint, jsonify, request

from trips.recommendation import generate_packing_list, get_trip_climate

from flask import Blueprint, jsonify, request, render_template

trips_bp = Blueprint("trips", __name__)

def _parse_trip_fields(data, defaults=None):
    defaults = defaults or {}
    city = data.get("city", defaults.get("city"))
    country = data.get("country", defaults.get("country"))
    start_date = datetime.strptime(data.get("start_date", defaults.get("start_date")), "%Y-%m-%d").date()
    end_date = datetime.strptime(data.get("end_date", defaults.get("end_date")), "%Y-%m-%d").date()
    accommodation_type = data.get("accommodation_type", defaults.get("accommodation_type", "hotel"))
    return city, country, start_date, end_date, accommodation_type


@trips_bp.route("/trips", methods=["POST"])
def create_trip():
    data = request.get_json(silent=True)
    

    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    city = data["city"]
    country = data["country"]
    start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
    end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
    accommodation_type = data.get("accommodation_type", "hotel")

    if end_date < start_date:
        return jsonify({"error": "end_date must be on or after start_date"}), 400

    trip_days = (end_date - start_date).days + 1

    from app import get_db
    db = get_db()

    location = db.execute(
        "SELECT id FROM locations WHERE city = ? AND country = ?", (city, country)
    ).fetchone()
    if location is None:
        return jsonify({"error": f"Unknown location: {city}, {country}"}), 404

    try:
        items = generate_packing_list(
            db=db, city=city, country=country,
            start_date=start_date, end_date=end_date, trip_days=trip_days,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    cursor = db.execute(
        "INSERT INTO trips (location_id, start_date, end_date, accommodation_type) "
        "VALUES (?, ?, ?, ?)",
        (location["id"], data["start_date"], data["end_date"], accommodation_type),
    )
    trip_id = cursor.lastrowid

    for item in items:
        db.execute(
            "INSERT INTO packing_items (trip_id, item_name, category, quantity, packed, source) "
            "VALUES (?, ?, ?, ?, 0, 'recommended')",
            (trip_id, item["item_name"], item["category"], item["quantity"]),
        )

    db.commit()

    return jsonify({"trip_id": trip_id, "items": items}), 201


@trips_bp.route("/trips/<int:trip_id>", methods=["GET"])
def get_trip(trip_id):
    from app import get_db
    db = get_db()

    trip = db.execute(
        "SELECT t.id, t.start_date, t.end_date, t.accommodation_type, l.city, l.country "
        "FROM trips t JOIN locations l ON t.location_id = l.id "
        "WHERE t.id = ?",
        (trip_id,),
    ).fetchone()
    if trip is None:
        return jsonify({"error": "Trip not found"}), 404

    items = db.execute(
        "SELECT id, item_name, category, quantity, packed, source "
        "FROM packing_items WHERE trip_id = ?",
        (trip_id,),
    ).fetchall()

    return jsonify({
        "trip": dict(trip),
        "items": [dict(item) for item in items],
    })

from flask import render_template


@trips_bp.route("/new", methods=["GET"])
def new_trip_page():
    return render_template("new_trip.html")


@trips_bp.route("/trips/<int:trip_id>/view", methods=["GET"])

def trip_view_page(trip_id):
    from app import get_db
    db = get_db()

    trip = db.execute(
        "SELECT t.id, t.start_date, t.end_date, t.accommodation_type, l.city, l.country "
        "FROM trips t JOIN locations l ON t.location_id = l.id WHERE t.id = ?",
        (trip_id,),
    ).fetchone()
    if trip is None:
        return "Trip not found", 404

    items = db.execute(
        "SELECT id, item_name, category, quantity, packed FROM packing_items WHERE trip_id = ?",
        (trip_id,),
    ).fetchall()

    try:
        climate = get_trip_climate(
            db, trip["city"], trip["country"],
            datetime.strptime(trip["start_date"], "%Y-%m-%d").date(),
            datetime.strptime(trip["end_date"], "%Y-%m-%d").date(),
        )
    except ValueError:
        climate = None

    return render_template("trip_view.html", trip=trip, items=items, climate=climate)

@trips_bp.route("/trips", methods=["GET"])
def list_trips_page():
    from app import get_db
    db = get_db()

    trips = db.execute(
        "SELECT t.id, t.start_date, t.end_date, l.city, l.country "
        "FROM trips t JOIN locations l ON t.location_id = l.id "
        "ORDER BY t.id DESC"
    ).fetchall()

    return render_template("trip_list.html", trips=trips)

@trips_bp.route("/api/cities", methods=["GET"])
def list_cities():
    from app import get_db
    db = get_db()
    country = request.args.get("country")

    if country:
        cities = db.execute(
            "SELECT DISTINCT city, country FROM locations WHERE country = ? ORDER BY city",
            (country,),
        ).fetchall()
    else:
        cities = db.execute("SELECT DISTINCT city, country FROM locations ORDER BY country, city").fetchall()

    return jsonify([dict(c) for c in cities])
@trips_bp.route("/api/countries", methods=["GET"])
def list_countries():
    from app import get_db
    db = get_db()
    countries = db.execute("SELECT DISTINCT country FROM locations ORDER BY country").fetchall()
    return jsonify([c["country"] for c in countries])

@trips_bp.route("/trips/<int:trip_id>", methods=["DELETE"])
def delete_trip(trip_id):
    from app import get_db
    db = get_db()

    trip = db.execute("SELECT id FROM trips WHERE id = ?", (trip_id,)).fetchone()
    if trip is None:
        return jsonify({"error": "Trip not found"}), 404

    db.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
    db.commit()

    return "", 204

@trips_bp.route("/trips/preview", methods=["POST"])
def preview_trip():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    city, country, start_date, end_date, _ = _parse_trip_fields(data)

    if end_date < start_date:
        return jsonify({"error": "end_date must be on or after start_date"}), 400

    trip_days = (end_date - start_date).days + 1

    from app import get_db
    db = get_db()

    location = db.execute(
        "SELECT id FROM locations WHERE city = ? AND country = ?", (city, country)
    ).fetchone()
    if location is None:
        return jsonify({"error": f"Unknown location: {city}, {country}"}), 404

    try:
        climate = get_trip_climate(db, city, country, start_date, end_date)
        items = generate_packing_list(
            db=db, city=city, country=country,
            start_date=start_date, end_date=end_date, trip_days=trip_days,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    return jsonify({"items": items, "climate": climate})

@trips_bp.route("/trips/<int:trip_id>", methods=["PUT"])
def edit_trip(trip_id):
    from app import get_db
    db = get_db()

    trip = db.execute("SELECT id FROM trips WHERE id = ?", (trip_id,)).fetchone()
    if trip is None:
        return jsonify({"error": "Trip not found"}), 404

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    city, country, start_date, end_date, accommodation_type = _parse_trip_fields(data)

    if end_date < start_date:
        return jsonify({"error": "end_date must be on or after start_date"}), 400

    trip_days = (end_date - start_date).days + 1

    location = db.execute(
        "SELECT id FROM locations WHERE city = ? AND country = ?", (city, country)
    ).fetchone()
    if location is None:
        return jsonify({"error": f"Unknown location: {city}, {country}"}), 404

    try:
        new_items = generate_packing_list(
            db=db, city=city, country=country,
            start_date=start_date, end_date=end_date, trip_days=trip_days,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    old_recommended = db.execute(
        "SELECT item_name, packed FROM packing_items WHERE trip_id = ? AND source = 'recommended'",
        (trip_id,),
    ).fetchall()
    packed_lookup = {row["item_name"]: row["packed"] for row in old_recommended}

    db.execute(
        "DELETE FROM packing_items WHERE trip_id = ? AND source = 'recommended'", (trip_id,)
    )

    for item in new_items:
        was_packed = packed_lookup.get(item["item_name"], 0)
        db.execute(
            "INSERT INTO packing_items (trip_id, item_name, category, quantity, packed, source) "
            "VALUES (?, ?, ?, ?, ?, 'recommended')",
            (trip_id, item["item_name"], item["category"], item["quantity"], was_packed),
        )

    db.execute(
        "UPDATE trips SET location_id = ?, start_date = ?, end_date = ?, accommodation_type = ? WHERE id = ?",
        (location["id"], data["start_date"], data["end_date"], accommodation_type, trip_id),
    )
    db.commit()

    return jsonify({"trip_id": trip_id, "items": new_items})