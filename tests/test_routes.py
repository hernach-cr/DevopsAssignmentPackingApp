def test_create_trip_returns_items(client):
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
    assert response.status_code == 201
    data = response.get_json()
    assert "trip_id" in data
    assert len(data["items"]) > 0


def test_create_trip_unknown_city_returns_404(client):
    response = client.post(
        "/trips",
        json={
            "city": "Nowhere",
            "country": "Nowhere",
            "start_date": "2026-06-15",
            "end_date": "2026-06-22",
        },
    )
    assert response.status_code == 404


def test_create_trip_bad_dates_returns_400(client):
    response = client.post(
        "/trips",
        json={
            "city": "Madrid",
            "country": "Spain",
            "start_date": "2026-06-22",
            "end_date": "2026-06-15",
        },
    )
    assert response.status_code == 400


def test_get_nonexistent_trip_returns_404(client):
    response = client.get("/trips/999999")
    assert response.status_code == 404

def test_preview_trip_returns_items_without_saving(client):
    response = client.post(
        "/trips/preview",
        json={
            "city": "Madrid",
            "country": "Spain",
            "start_date": "2026-06-15",
            "end_date": "2026-06-22",
            "accommodation_type": "hotel",
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["items"]) > 0
    assert "trip_id" not in data

    trips_list = client.get("/trips")
    assert b"Madrid" not in trips_list.data


def test_preview_trip_unknown_city_returns_404(client):
    response = client.post(
        "/trips/preview",
        json={
            "city": "Nowhere",
            "country": "Nowhere",
            "start_date": "2026-06-15",
            "end_date": "2026-06-22",
        },
    )
    assert response.status_code == 404

def test_edit_trip_updates_destination_and_regenerates_items(client):
    create_response = client.post(
        "/trips",
        json={
            "city": "Madrid",
            "country": "Spain",
            "start_date": "2026-06-15",
            "end_date": "2026-06-22",
            "accommodation_type": "hotel",
        },
    )
    trip_id = create_response.get_json()["trip_id"]

    edit_response = client.put(
        f"/trips/{trip_id}",
        json={
            "city": "Miami",
            "country": "United States",
            "start_date": "2026-07-01",
            "end_date": "2026-07-10",
            "accommodation_type": "hotel",
        },
    )
    assert edit_response.status_code == 200

    trip_response = client.get(f"/trips/{trip_id}")
    data = trip_response.get_json()
    assert data["trip"]["city"] == "Miami"
    names = [item["item_name"] for item in data["items"]]
    assert "T-shirt" in names
    assert "Jacket" not in names


def test_edit_trip_preserves_custom_items(client):
    create_response = client.post(
        "/trips",
        json={
            "city": "Madrid",
            "country": "Spain",
            "start_date": "2026-06-15",
            "end_date": "2026-06-22",
        },
    )
    trip_id = create_response.get_json()["trip_id"]

    client.post(f"/trips/{trip_id}/items", json={"item_name": "Passport"})

    client.put(
        f"/trips/{trip_id}",
        json={
            "city": "Miami",
            "country": "United States",
            "start_date": "2026-07-01",
            "end_date": "2026-07-10",
        },
    )

    trip_response = client.get(f"/trips/{trip_id}")
    names = [item["item_name"] for item in trip_response.get_json()["items"]]
    assert "Passport" in names


def test_edit_trip_preserves_packed_status_for_matching_items(client):
    create_response = client.post(
        "/trips",
        json={
            "city": "Madrid",
            "country": "Spain",
            "start_date": "2026-06-15",
            "end_date": "2026-06-22",
        },
    )
    trip_id = create_response.get_json()["trip_id"]

    items_before = client.get(f"/trips/{trip_id}").get_json()["items"]
    tshirt = next(i for i in items_before if i["item_name"] == "T-shirt")
    client.patch(f"/items/{tshirt['id']}", json={"packed": True})

    client.put(
        f"/trips/{trip_id}",
        json={
            "city": "Barcelona",
            "country": "Spain",
            "start_date": "2026-06-15",
            "end_date": "2026-06-22",
        },
    )

    items_after = client.get(f"/trips/{trip_id}").get_json()["items"]
    tshirt_after = next(i for i in items_after if i["item_name"] == "T-shirt")
    assert tshirt_after["packed"] == 1


def test_edit_nonexistent_trip_returns_404(client):
    response = client.put(
        "/trips/999999",
        json={"city": "Madrid", "country": "Spain", "start_date": "2026-06-15", "end_date": "2026-06-22"},
    )
    assert response.status_code == 404