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