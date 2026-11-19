import os
import requests

TRIPS_URL = os.environ.get("TRIPS_URL", "http://localhost:5001")
PACKS_URL = os.environ.get("PACKS_URL", "http://localhost:5002")

MADRID = {"city": "Madrid", "country": "Spain",
          "start_date": "2026-06-15", "end_date": "2026-06-22"}


def test_trips_checks_packs():
   
    r = requests.post(f"{TRIPS_URL}/trips", json=MADRID, timeout=5)
    assert r.status_code == 201
    trip_id = r.json()["trip_id"]

    items = requests.get(f"{PACKS_URL}/trips/{trip_id}/items", timeout=5).json()
    assert len(items) > 0
    assert all(i["source"] == "recommended" for i in items)

    requests.delete(f"{TRIPS_URL}/trips/{trip_id}", timeout=5)

def test_packs_checks_trips():
    trip_id = requests.post(f"{TRIPS_URL}/trips", json=MADRID, timeout=5).json()["trip_id"]

  
    r = requests.post(f"{PACKS_URL}/trips/{trip_id}/items", json={"item_name": "Charger"}, timeout=5)
    assert r.status_code == 201

   
    r = requests.post(f"{PACKS_URL}/trips/999999/items", json={"item_name": "Charger"}, timeout=5)
    assert r.status_code == 404

    requests.delete(f"{TRIPS_URL}/trips/{trip_id}", timeout=5)


def test_delete_tripremovespacks():
    
    r = requests.post(f"{TRIPS_URL}/trips", json=MADRID, timeout=5)
    assert r.status_code == 201
    trip_id = r.json()["trip_id"]

    requests.delete(f"{TRIPS_URL}/trips/{trip_id}", timeout=5)
    items = requests.get(f"{PACKS_URL}/trips/{trip_id}/items", timeout=5).json()
    assert len(items) == 0
    assert r.status_code == 201

def test_edit_tripkeepscustom():
   
  
    trip_id = requests.post(f"{TRIPS_URL}/trips", json=MADRID, timeout=5).json()["trip_id"]

    requests.post(f"{PACKS_URL}/trips/{trip_id}/items", json={"item_name": "Wallet"}, timeout=5)

  
    miami = {"city": "Miami", "country": "United States",
             "start_date": "2026-07-01", "end_date": "2026-07-10"}
    r = requests.put(f"{TRIPS_URL}/trips/{trip_id}", json=miami, timeout=5)
    assert r.status_code == 200


    items = requests.get(f"{PACKS_URL}/trips/{trip_id}/items", timeout=5).json()
    names = [i["item_name"] for i in items]
    assert "Wallet" in names

    requests.delete(f"{TRIPS_URL}/trips/{trip_id}", timeout=5)