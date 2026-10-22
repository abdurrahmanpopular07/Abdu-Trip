"""
TripGenius — distance & intercity travel cost estimation.

Distance is computed with the haversine (great-circle) formula between the
traveller's starting point and the destination, then scaled up by a fixed
"road factor" since real roads are never a straight line.

Travel cost is then estimated per mode using simple, transparent
assumptions (fuel price, vehicle mileage, or per-km fare) — deliberately
explainable rather than pulled from a live pricing API, so it's easy to
defend in a viva: every number traces back to a stated assumption.
"""

import math

ROAD_DISTANCE_FACTOR = 1.30  # real road distance vs. straight-line distance

# Editable assumptions — shown to the user alongside the estimate.
TRAVEL_MODES = {
    "car": {
        "label": "Car",
        "kind": "fuel",
        "mileage_kmpl": 15,
        "fuel_price_per_l": 100,
        "note": "Assumes a petrol car at ~15 km/l and fuel at ~₹100/L.",
    },
    "bike": {
        "label": "Bike",
        "kind": "fuel",
        "mileage_kmpl": 40,
        "fuel_price_per_l": 100,
        "note": "Assumes a petrol bike at ~40 km/l and fuel at ~₹100/L.",
    },
    "bus": {
        "label": "Bus",
        "kind": "fare",
        "fare_per_km": 1.5,
        "note": "Assumes an average intercity bus fare of ~₹1.5/km per person.",
    },
    "train": {
        "label": "Train",
        "kind": "fare",
        "fare_per_km": 1.1,
        "note": "Assumes an average sleeper/AC-mix train fare of ~₹1.1/km per person.",
    },
}


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two lat/lon points, in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (math.sin(d_phi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def estimate_road_distance_km(lat1, lon1, lat2, lon2):
    """One-way approximate road distance, in km."""
    straight = haversine_km(lat1, lon1, lat2, lon2)
    return straight * ROAD_DISTANCE_FACTOR


def estimate_travel_cost(one_way_distance_km, mode_key):
    """
    Returns (cost_in_rupees, detail_string) for a ROUND TRIP using the given
    mode, based on the one-way road distance.
    """
    if mode_key not in TRAVEL_MODES:
        raise ValueError(f"Unknown travel mode: {mode_key}")

    mode = TRAVEL_MODES[mode_key]
    round_trip_km = one_way_distance_km * 2

    if mode["kind"] == "fuel":
        litres = round_trip_km / mode["mileage_kmpl"]
        cost = litres * mode["fuel_price_per_l"]
        detail = f"~{litres:.1f} L fuel for {round_trip_km:.0f} km round trip"
    else:
        cost = round_trip_km * mode["fare_per_km"]
        detail = f"~₹{mode['fare_per_km']}/km fare for {round_trip_km:.0f} km round trip"

    return round(cost), detail
