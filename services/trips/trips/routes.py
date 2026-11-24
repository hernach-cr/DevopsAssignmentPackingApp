from datetime import datetime



from trips.recommendation import generate_packing_list, get_trip_climate

from flask import Blueprint, current_app, jsonify, request

from trips import packs_client

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
        "SELECT id FROM locations WHERE city = %s AND country = %s", (city, country)
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
        "VALUES (%s, %s, %s, %s)",
        (location["id"], data["start_date"], data["end_date"], accommodation_type),
    )
    trip_id = int(cursor.lastrowid)

    

    db.commit()
    saved = packs_client.replace_recommended(trip_id,items)
    return jsonify({"trip_id": trip_id, "items": items, "packing_list_saved": saved}), 201


@trips_bp.route("/trips/<int:trip_id>", methods=["GET"])
def get_trip(trip_id):
    from app import get_db
    db = get_db()

    trip = db.execute(
        "SELECT t.id, t.start_date, t.end_date, t.accommodation_type, l.city, l.country "
        "FROM trips t JOIN locations l ON t.location_id = l.id "
        "WHERE t.id = %s",
        (trip_id,),
    ).fetchone()
    if trip is None:
        return jsonify({"error": "Trip not found"}), 404

    try:
        climate = get_trip_climate(
            db, trip["city"], trip["country"],
            datetime.strptime(trip["start_date"], "%Y-%m-%d").date(),
            datetime.strptime(trip["end_date"], "%Y-%m-%d").date(),
        )
    except ValueError:
        climate = None

    return jsonify({"trip": dict(trip), "climate": climate})


@trips_bp.route("/trips", methods=["GET"])
def list_trips_page():
    from app import get_db
    db = get_db()

    trips = db.execute(
        "SELECT t.id, t.start_date, t.end_date, l.city, l.country "
        "FROM trips t JOIN locations l ON t.location_id = l.id "
        "ORDER BY t.id DESC"
    ).fetchall()

    return jsonify([dict(trip) for trip in trips])

@trips_bp.route("/api/cities", methods=["GET"])
def list_cities():
    from app import get_db
    db = get_db()
    country = request.args.get("country")

    if country:
        cities = db.execute(
            "SELECT DISTINCT city, country FROM locations WHERE country = %s ORDER BY city",
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

    trip = db.execute("SELECT id FROM trips WHERE id = %s", (trip_id,)).fetchone()
    if trip is None:
        return jsonify({"error": "Trip not found"}), 404

    db.execute("DELETE FROM trips WHERE id = %s", (trip_id,))
    db.commit()
    deleted = packs_client.delete_items(trip_id)
    if not deleted:
        current_app.logger.warning("Trip %s deleted but its items could not be removed from packs", trip_id)
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
        "SELECT id FROM locations WHERE city = %s AND country = %s", (city, country)
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

    trip = db.execute("SELECT id FROM trips WHERE id = %s", (trip_id,)).fetchone()
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
        "SELECT id FROM locations WHERE city = %s AND country = %s", (city, country)
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

     

    db.execute(
        "UPDATE trips SET location_id = %s, start_date = %s, end_date = %s, accommodation_type = %s WHERE id = %s",
        (location["id"], data["start_date"], data["end_date"], accommodation_type, trip_id),
    )
    db.commit()
    saved = packs_client.replace_recommended(trip_id,new_items)
    return jsonify({"trip_id": trip_id, "items": new_items, "packing_list_saved": saved})