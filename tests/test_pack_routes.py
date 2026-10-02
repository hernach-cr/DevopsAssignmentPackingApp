import json


def _create_trip(client):
    response = client.post(
        "/trips",
        json={
            "city": "Madrid",
            "country": "Spain",
            "start_date": "2026-06-15",
            "end_date": "2026-06-22",
            "accommodation_type": "hotel",
        },
    )
    return response.get_json()["trip_id"]


def test_add_item_creates_custom_item(client):
    trip_id = _create_trip(client)

    response = client.post(
        f"/trips/{trip_id}/items",
        json={"item_name": "Laptop charger", "category": "other", "quantity": 1},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["item_name"] == "Laptop charger"
    assert data["source"] == "custom"
    assert data["packed"] is False


def test_add_item_to_nonexistent_trip_returns_404(client):
    response = client.post(
        "/trips/999999/items",
        json={"item_name": "Laptop charger"},
    )
    assert response.status_code == 404


def test_update_item_toggles_packed(client):
    trip_id = _create_trip(client)
    add_response = client.post(f"/trips/{trip_id}/items", json={"item_name": "Charger"})
    item_id = add_response.get_json()["id"]

    response = client.patch(f"/items/{item_id}", json={"packed": True})
    assert response.status_code == 200
    assert response.get_json()["packed"] == 1


def test_update_item_changes_quantity_without_affecting_packed(client):
    trip_id = _create_trip(client)
    add_response = client.post(f"/trips/{trip_id}/items", json={"item_name": "Charger"})
    item_id = add_response.get_json()["id"]

    client.patch(f"/items/{item_id}", json={"packed": True})
    response = client.patch(f"/items/{item_id}", json={"quantity": 3})

    data = response.get_json()
    assert data["quantity"] == 3
    assert data["packed"] == 1


def test_update_item_rejects_zero_quantity(client):
    trip_id = _create_trip(client)
    add_response = client.post(f"/trips/{trip_id}/items", json={"item_name": "Charger"})
    item_id = add_response.get_json()["id"]

    response = client.patch(f"/items/{item_id}", json={"quantity": 0})
    assert response.status_code == 400


def test_update_nonexistent_item_returns_404(client):
    response = client.patch("/items/999999", json={"packed": True})
    assert response.status_code == 404


def test_delete_item_removes_it(client):
    trip_id = _create_trip(client)
    add_response = client.post(f"/trips/{trip_id}/items", json={"item_name": "Charger"})
    item_id = add_response.get_json()["id"]

    delete_response = client.delete(f"/items/{item_id}")
    assert delete_response.status_code == 204

    trip_response = client.get(f"/trips/{trip_id}")
    item_ids = [item["id"] for item in trip_response.get_json()["items"]]
    assert item_id not in item_ids


def test_delete_nonexistent_item_returns_404(client):
    response = client.delete("/items/999999")
    assert response.status_code == 404