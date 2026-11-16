import os
import requests

PACKS_URL = os.environ.get("PACKS_URL", "http://localhost:5002")
TIMEOUT = 2  


def replace_recommended(trip_id, items):
    try:
        r = requests.put(
            f"{PACKS_URL}/trips/{trip_id}/items/recommended",
            json=items,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return True
    except requests.RequestException:
        return False

def list_items(trip_id):
    try:
        r = requests.get(                         
            f"{PACKS_URL}/trips/{trip_id}/items",  
            timeout=TIMEOUT,                     
        )
        r.raise_for_status()
        return r.json()                              
    except requests.RequestException:
        return None       

def delete_items(trip_id):
    try:
        r = requests.delete(
            f"{PACKS_URL}/trips/{trip_id}/items",
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return True
    except requests.RequestException:
        return False