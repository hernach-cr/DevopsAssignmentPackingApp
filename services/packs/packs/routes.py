from flask import Blueprint, jsonify, request

packing_bp = Blueprint("packing", __name__)


@packing_bp.route("/trips/<int:trip_id>/items", methods=["POST"])
def add_item(trip_id):
    from app import get_db
    db = get_db()

    trip = db.execute("SELECT id FROM trips WHERE id = ?", (trip_id,)).fetchone()
    if trip is None:
        return jsonify({"error": "Trip not found"}), 404

    data = request.get_json(silent=True)
    if data is None or "item_name" not in data:
        return jsonify({"error": "item_name is required"}), 400

    item_name = data["item_name"]
    category = data.get("category", "other")
    quantity = data.get("quantity", 1)

    cursor = db.execute(
        "INSERT INTO packing_items (trip_id, item_name, category, quantity, packed, source) "
        "VALUES (?, ?, ?, ?, 0, 'custom')",
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

    item = db.execute("SELECT id FROM packing_items WHERE id = ?", (item_id,)).fetchone()
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    if "packed" in data:
        db.execute(
            "UPDATE packing_items SET packed = ? WHERE id = ?",
            (1 if data["packed"] else 0, item_id),
        )

    if "quantity" in data:
        if data["quantity"] < 1:
            return jsonify({"error": "quantity must be at least 1"}), 400
        db.execute(
            "UPDATE packing_items SET quantity = ? WHERE id = ?",
            (data["quantity"], item_id),
        )

    db.commit()

    updated = db.execute(
        "SELECT id, item_name, category, quantity, packed, source FROM packing_items WHERE id = ?",
        (item_id,),
    ).fetchone()
    return jsonify(dict(updated))


@packing_bp.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    from app import get_db
    db = get_db()

    item = db.execute("SELECT id FROM packing_items WHERE id = ?", (item_id,)).fetchone()
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    db.execute("DELETE FROM packing_items WHERE id = ?", (item_id,))
    db.commit()

    return "", 204