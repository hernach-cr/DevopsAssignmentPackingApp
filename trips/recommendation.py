import math

LAUNDRY_AFTER_DAYS = 8


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


COASTAL_CITIES = {
    ("Barcelona", "Spain"), ("Valencia", "Spain"), ("Bilbao", "Spain"),
    ("Lisbon", "Portugal"), ("Porto", "Portugal"),
    ("Marseille", "France"),
    ("Naples", "Italy"), ("Venice", "Italy"), ("Rome", "Italy"),
    ("Athens", "Greece"),
    ("Amsterdam", "Netherlands"),
    ("Casablanca", "Morocco"), ("Algiers", "Algeria"), ("Tunis", "Tunisia"),
    ("Lagos", "Nigeria"), ("Accra", "Ghana"),
    ("Dar es Salaam", "Tanzania"), ("Cape Town", "South Africa"),
    ("Dubai", "United Arab Emirates"),
    ("Mumbai", "India"), ("Karachi", "Pakistan"), ("Colombo", "Sri Lanka"),
    ("Singapore", "Singapore"), ("Jakarta", "Indonesia"), ("Manila", "Philippines"),
    ("Taipei", "Taiwan"),
    ("Sydney", "Australia"), ("Melbourne", "Australia"), ("Perth", "Australia"),
    ("Auckland", "New Zealand"), ("Wellington", "New Zealand"),
    ("Rio de Janeiro", "Brazil"), ("Salvador", "Brazil"),
    ("Montevideo", "Uruguay"), ("Lima", "Peru"), ("Caracas", "Venezuela"),
    ("Miami", "United States"), ("Los Angeles", "United States"),
    ("Houston", "United States"),
}

COASTAL_RULES = [
    ("Swimsuit", "other", 0.3, 2),
    ("Beach towel", "other", 0, 1),
    ("Sandals", "footwear", 0, 1),
    ("suncream","other", 0 , 1)
]

minimum_temp = 20
max_precipitation = 200

RAIN_RULES = {
    "wet": [
        ("Raincoat", "outerwear", 0, 1),
        ("Umbrella", "other", 0, 1),
    ],
    "moderate": [],
    "dry": [],
    None: [],
}

def is_coastal(city, country):
    return (city, country) in COASTAL_CITIES

def wants_beach_items(city, country, avg_temp_c, precip_mm):
    if not is_coastal(city, country):
        return False
    if avg_temp_c <= minimum_temp:
        return False
    if precip_mm is not None and precip_mm > max_precipitation:
        return False
    return True

TEMPERATURE_RULES = {
    "cool": [
        ("T-shirt", "top", 0.5, 1),
        ("Long-sleeve shirt", "top", 0.5, 1),
        ("Sweater", "top", 0.5, 1),
        ("Jeans", "bottom", 0.75, 1),
        ("Sneakers", "footwear", 0.25, 1),
        ("Underwear", "other", 1.0, 1),
        ("Socks", "other", 1.0, 1),
    ],
    
    "cold": [
        ("Jacket", "outerwear", 0.5, 1),
        ("Coat", "outerwear", 0, 1),
        ("Shirt", "top", 0.5, 1),
        ("Thermal t-shirt", "top", 0.25, 1),
        ("Jeans", "bottom", 0.75, 1),
        ("Sneakers", "footwear", 0.5, 1),
        ("Underwear", "other", 1.0, 1),
        ("Socks", "other", 1.0, 1),
    ],
    
    "freezing": [
        ("Gloves", "other", 0, 1),
        ("Scarf", "other", 0, 1),
        ("Thermal leggings", "bottom", 0.5, 1),
        ("Thermal t-shirt", "top", 0.75, 1),
        ("Shirt", "top", 0.5, 1),
        ("Jacket", "outerwear", 0.5, 1),
        ("Coat", "outerwear", 0, 1),
        ("Sneakers", "footwear", 0.25, 1),
        ("Boots", "footwear", 0.25, 1),
        ("Underwear", "other", 1.0, 1),
        ("Socks", "other", 1.0, 1),
    ],
    "mild": [
        ("T-shirt", "top", 0.75, 1),
        ("Light jacket", "outerwear", 0.25, 1),
        ("Jeans", "bottom", 0.5, 1),
        ("Shorts", "bottom", 0.5, 1),
        ("Sneakers", "footwear", 0.5, 1),
        ("Underwear", "other", 1.0, 1),
        ("Socks", "other", 1.0, 1),
    ],
    "hot": [
        ("T-shirt", "top", 1.0, 1),
        ("Shorts", "bottom", 0.75, 1),
        ("Sandals", "footwear", 0, 1),
        ("Sneakers", "footwear", 0.33, 1),
        ("Sunglasses", "other", 0, 1),
        ("Underwear", "other", 1.0, 1),
        ("Socks", "other", 1.0, 1),
],


}