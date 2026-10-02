from datetime import datetime

from flask import Blueprint, jsonify, request

from trips.recommendation import generate_packing_list

trips_bp = Blueprint("trips", __name__)


@trips_bp.route("/trips", methods=["POST"])
def create_trip():
    data = request.get_json(silent=True)
    print("Received data:", data)

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