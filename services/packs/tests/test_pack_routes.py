import json


def _create_trip(client):
    return 1 


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


def test_add_item_to_nonexistent_trip_returns_404(client, fake_trips):
    fake_trips["answer"] = False 
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

    items_response = client.get(f"/trips/{trip_id}/items")
    item_ids = [item["id"] for item in items_response.get_json()]
    assert item_id not in item_ids


def test_delete_nonexistent_item_returns_404(client):
    response = client.delete("/items/999999")
    assert response.status_code == 404


def test_1_endpoints_packs_incasetripsdown(client, fake_trips):
    fake_trips["answer"] = None
    response = client.post("/trips/1/items", json={"item_name": "Charger"})
    assert response.status_code == 201

def test_2_endpoints_packs_replacebutkeepitems(client):
    client.post("/trips/1/items", json={"item_name": "Computer"})      
    client.put("/trips/1/items/recommended",
               json=[{"item_name": "T-shirt", "category": "top", "quantity": 3}])

    names = [i["item_name"] for i in client.get("/trips/1/items").get_json()]
    assert "Computer" in names

def test_3_endpoints_packs_replacebutkeepticks(client):   
    client.put("/trips/1/items/recommended",
               json=[{"item_name": "T-shirt", "category": "top", "quantity": 3}])
    items = client.get("/trips/1/items").get_json()
    tshirt = next(i for i in items if i["item_name"] == "T-shirt")
    client.patch(f"/items/{tshirt['id']}", json={"packed": True })
    client.put("/trips/1/items/recommended",
               json=[{"item_name": "T-shirt", "category": "top", "quantity": 3},
                     {"item_name": "Umbrella", "category": "other", "quantity": 1}])
    items_after = client.get("/trips/1/items").get_json()
    tshirt_after = next(i for i in items_after if i["item_name"] == "T-shirt")
    assert tshirt_after["packed"] == 1

def test_4_endpoints_packs_rejectsnotlist(client):
    response = client.put("/trips/1/items/recommended", json={"item_name": "x"})
    assert response.status_code == 400

def test_5_endpoints_packs_deleteitemsremovesall(client):
    client.post("/trips/1/items", json={"item_name": "Charger"})
    client.post("/trips/1/items", json={"item_name": "Passport"})

    response = client.delete("/trips/1/items")
    assert response.status_code == 204

    assert client.get("/trips/1/items").get_json() == []