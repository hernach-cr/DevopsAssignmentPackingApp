from trips.recommendation import (
    temperature,
    rain,
    effective_days,
    item_quantity,
    beach_items,
    recommend_clothing,
)
from datetime import date
import pytest
from trips.recommendation import generate_packing_list

def test_temperature_boundaries():
    assert temperature(-5) == "freezing"
    assert temperature(0) == "cold"
    assert temperature(9) == "cold"
    assert temperature(10) == "cool"
    assert temperature(17) == "mild"
    assert temperature(25) == "mild"
    assert temperature(30) == "hot"

def test_rain_boundaries():
    assert rain(None) is None
    assert rain(0) == "dry"
    assert rain(49) == "dry"
    assert rain(50) == "moderate"
    assert rain(100) == "moderate"
    assert rain(150) == "wet"

def test_effective_days():
    assert effective_days(3) == 3
    assert effective_days(7) == 7
    assert effective_days(8) == 8
    assert effective_days(10) == 8



def test_item_quantity_roundingandminimum():
    assert item_quantity(per_day=0.5, minimum=1, days=4) == 2
    assert item_quantity(per_day=0, minimum=1, days=7) == 1
    assert item_quantity(per_day=0.33, minimum=1, days=3) == 1
    assert item_quantity(per_day=0.33, minimum=1, days=4) == 2

def test_beach_items_requires_coastalwarm_and_not_too_wet():
    assert beach_items("Barcelona", "Spain", 26, 30) is True
    assert beach_items("Barcelona", "Spain", 20, 30) is False   
    assert beach_items("Madrid", "Spain", 30, 10) is False     
    assert beach_items("Miami", "United States", 28, 201) is False  
    assert beach_items("Miami", "United States", 28, 200) is True   
    assert beach_items("Dubai", "United Arab Emirates", 35, None) 

def test_recommend_clothing_cold_inland():
    result = recommend_clothing(avg_temp_c=8, precip_mm=30, trip_days=5, city="Madrid", country="Spain")
    names = [item["item_name"] for item in result]

    assert "Coat" in names
    assert "Raincoat" not in names
    assert "Swimsuit" not in names

def test_recommend_clothing_hotwet_inland():
    result = recommend_clothing(avg_temp_c=27, precip_mm=150, trip_days=5, city="Madrid", country="Spain")
    names = [item["item_name"] for item in result]

    assert "Coat" not in names
    assert "Raincoat"  in names
    assert "Swimsuit"  not in names



def test_generate_packing_list_looks_up_correct_month(test_db):
    items = generate_packing_list(
        db=test_db,
        city="Madrid",
        country="Spain",
        start_date=date(2026, 6, 15),
        end_date=date(2026, 6, 22),
        trip_days=8,
    )
    names = [item["item_name"] for item in items]

    assert "T-shirt" in names
    assert "Coat" not in names


def test_generate_packing_list_raises_for_unknown_city(test_db):
    with pytest.raises(ValueError):
        generate_packing_list(
            db=test_db,
            city="Nowhere",
            country="Nowhere",
            start_date=date(2026, 6, 15),
            end_date=date(2026, 6, 22),
            trip_days=8,
        )