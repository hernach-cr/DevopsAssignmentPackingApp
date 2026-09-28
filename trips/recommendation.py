import math

LAUNDRY_AFTER_DAYS = 7


def effective_days(trip_days):
    if trip_days > LAUNDRY_AFTER_DAYS:
        return LAUNDRY_AFTER_DAYS
    else:
        return trip_days

def item_quantity(per_day, minimum, days):
    quantity = math.ceil(per_day * days)

    if quantity < minimum:
        quantity = minimum

    return quantity

def temperature(avg_temp_c):
    if avg_temp_c < 0:
        return "freezing"
    elif 0 <= avg_temp_c < 10:
        return "cold"
    elif 10 <= avg_temp_c < 17:
        return "cool"
    elif 17 <= avg_temp_c <= 25:
        return "mild"
    else:
        return "hot"

def rain(precip_mm):
    if precip_mm is None:
        return None
    elif precip_mm > 100:
        return "wet"
    elif 50 <= precip_mm <= 100:
        return "moderate"
    else:
        return "dry"