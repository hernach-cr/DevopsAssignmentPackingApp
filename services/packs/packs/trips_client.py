import os
import requests


TRIPS_URL = os.environ.get("TRIPS_URL", "http://localhost:5001")
TIMEOUT = 2


def trip_exists(trip_id):
    try:
        r = requests.get(
            f"{TRIPS_URL}/trips/{trip_id}",
            timeout=TIMEOUT,
        )
    except requests.RequestException:
        return None

    if r.status_code == 200:
        return True
    if r.status_code == 404:
        return False
    return None
