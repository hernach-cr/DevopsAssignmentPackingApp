from flask import Blueprint, jsonify, request, current_app
from packs import trips_client

packing_bp = Blueprint("packing", __name__)


@packing_bp.route("/trips/<int:trip_id>/items", methods=["POST"])
def add_item(trip_id):
    from app import get_db
    db = get_db()

    exists = trips_client.trip_exists(trip_id)
    if exists is False:
        return jsonify({"error": "Trip not found"}), 404
    if exists is None:
        current_app.logger.warning("Trips unavailable, adding item to trip %s without checking", trip_id)

    data = request.get_json(silent=True)
    if data is None or "item_name" not in data:
        return jsonify({"error": "item_name is required"}), 400

    item_name = data["item_name"]
    category = data.get("category", "other")
    quantity = data.get("quantity", 1)

    cursor = db.execute(
        "INSERT INTO packing_items (trip_id, item_name, category, quantity, packed, source) "
        "VALUES (%s, %s, %s, %s, 0, 'custom')",
        (trip_id, item_name, category, quantity),
    )
    db.commit()

    return jsonify({
        "id": cursor.lastrowid,
        "item_name": item_name,
        "category": category,
        "quantity": quantity,
        "packed": False,
        "source": "custom",
    }), 201


@packing_bp.route("/items/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    from app import get_db
    db = get_db()

    item = db.execute("SELECT id FROM packing_items WHERE id = %s", (item_id,)).fetchone()
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    if "packed" in data:
        db.execute(
            "UPDATE packing_items SET packed = %s WHERE id = %s",
            (1 if data["packed"] else 0, item_id),
        )

    if "quantity" in data:
        if data["quantity"] < 1:
            return jsonify({"error": "quantity must be at least 1"}), 400
        db.execute(
            "UPDATE packing_items SET quantity = %s WHERE id = %s",
            (data["quantity"], item_id),
        )

    db.commit()

    updated = db.execute(
        "SELECT id, item_name, category, quantity, packed, source FROM packing_items WHERE id = %s",
        (item_id,),
    ).fetchone()
    return jsonify(dict(updated))


@packing_bp.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    from app import get_db
    db = get_db()

    item = db.execute("SELECT id FROM packing_items WHERE id = %s", (item_id,)).fetchone()
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    db.execute("DELETE FROM packing_items WHERE id = %s", (item_id,))
    db.commit()

    return "", 204

@packing_bp.route("/trips/<int:trip_id>/items", methods=["GET" ])
def list_items(trip_id):
    from app import get_db
    db=get_db()

    rows=db.execute(
        "SELECT id, item_name, category, quantity, packed, source FROM packing_items WHERE trip_id=%s",
        (trip_id,),).fetchall()

    items=[dict(row) for row in rows]
    return jsonify(items)


@packing_bp.route("/trips/<int:trip_id>/items", methods=["DELETE"])
def delete_trip_items(trip_id):
    from app import get_db
    db = get_db()
    db.execute("DELETE FROM packing_items WHERE trip_id = %s", (trip_id,))
    db.commit()
    return "", 204

@packing_bp.route("/trips/<int:trip_id>/items/recommended", methods=["PUT"])
def replace_recommended(trip_id):
    from app import get_db
    db = get_db()

    new_items = request.get_json(silent=True)
    if not isinstance(new_items, list):
        return jsonify({"error": "Body must be a JSON list of items"}), 400

    old_recommended= db.execute(
        "SELECT item_name, packed FROM packing_items WHERE trip_id = %s AND source = 'recommended'",
        (trip_id,),
    ).fetchall()
    packed_lookup = {}
    packed_lookup = {}
    for row in old_recommended:
        packed_lookup[row["item_name"]] = row["packed"]

    db.execute(
        "DELETE FROM packing_items WHERE trip_id = %s AND source = 'recommended'", (trip_id,)
    )
    for item in new_items:
            was_packed = packed_lookup.get(item["item_name"], 0)
            db.execute(
                "INSERT INTO packing_items (trip_id, item_name, category, quantity, packed, source) "
                "VALUES (%s, %s, %s, %s, %s, 'recommended')",
                (trip_id, item["item_name"], item["category"], item["quantity"], was_packed),
            )
    db.commit()
    return jsonify(new_items), 200