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

def test_edit_trip_updates_destination_and_regenerates_items(client, fake_packs):
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
    assert trip_response.get_json()["trip"]["city"] == "Miami"

    sent_trip_id, sent_items = fake_packs["replace"][-1]
    assert sent_trip_id == trip_id
    names = [item["item_name"] for item in sent_items]
    assert "T-shirt" in names
    assert "Jacket" not in names


def test_edit_nonexistent_trip_returns_404(client):
    response = client.put(
        "/trips/999999",
        json={"city": "Madrid", "country": "Spain", "start_date": "2026-06-15", "end_date": "2026-06-22"},
    )
    assert response.status_code == 404

MADRID = {"city": "Madrid", "country": "Spain",
          "start_date": "2026-06-15", "end_date": "2026-06-22"}


def test_1_endpoints_trips_create_trip_when_packs_down(client, fake_packs):
    fake_packs["up"] = False
    response = client.post("/trips", json=MADRID)
    assert response.status_code == 201
    assert response.get_json()["packing_list_saved"] is False

def test_2_endpoints_trips_createtrip_sendslisttopacks(client, fake_packs):
    response = client.post("/trips", json=MADRID)
    trip_id = response.get_json()["trip_id"]

    assert len(fake_packs["replace"]) == 1
    sent_trip_id, sent_items = fake_packs["replace"][0]
    assert sent_trip_id == trip_id
    assert len(sent_items) > 0


def test_3_endpoints_trips_delete_trip_packsdeleteitems(client, fake_packs):
    trip_id = client.post("/trips", json=MADRID).get_json()["trip_id"]

    response = client.delete(f"/trips/{trip_id}")
    assert response.status_code == 204
    assert trip_id in fake_packs["delete"]


def test_4_endpoints_trips_includes_climate(client):
    trip_id = client.post("/trips", json=MADRID).get_json()["trip_id"]

    data = client.get(f"/trips/{trip_id}").get_json()
    assert "climate" in data
    assert "items" not in data