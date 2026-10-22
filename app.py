"""
TripGenius — AI Travel Planner backend.

Internship project domain: Data Science & AI/ML using Python.

Two pieces of "intelligence" work together on every request:
  1. A trained Linear Regression model (see model/train_model.py) predicts
     a realistic estimated total spend for the trip from engineered features.
  2. A rule-based content recommender composes a day-by-day itinerary and a
     budget split, using a small curated knowledge base (data/knowledge_base.py).

Run:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000
"""

import os
import re
import json
import pickle
import random
from functools import wraps

from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, flash
)

from data.knowledge_base import (
    DESTINATIONS, BUDGET_SPLIT, ACTIVITY_POOL, DAY_THEME_TEMPLATES
)
from model.train_model import train_and_save, _featurize
from travel import estimate_road_distance_km, estimate_travel_cost, TRAVEL_MODES
from images import get_destination_image_url
import pandas as pd
import auth_db

APP_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(APP_DIR, "model", "trip_cost_model.pkl")

app = Flask(__name__)
# Used to sign the session cookie. Set a real secret via the
# TRIPGENIUS_SECRET_KEY env var before deploying this anywhere public.
app.secret_key = os.environ.get("TRIPGENIUS_SECRET_KEY", "dev-secret-change-me")

auth_db.init_db()

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Please log in to plan a trip.", "login_required": True}), 401
            flash("Please log in to plan a trip.")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_user():
    return {"current_user_name": session.get("user_name")}


def load_model():
    """Load the trained model, training it on first run if missing."""
    if not os.path.exists(MODEL_PATH):
        train_and_save(MODEL_PATH)
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


MODEL_BUNDLE = load_model()

# Below this fraction of the true required cost, the trip is not feasible —
# reject with a clear error instead of silently showing a huge shortfall.
MIN_FEASIBLE_RATIO = 0.55
# Above this fraction over the required cost, tell the user they have real
# surplus room (not just "within budget").
SURPLUS_RATIO = 1.30


def predict_estimated_cost(days, budget, tier, style):
    row = pd.DataFrame([{
        "days": days,
        "budget": budget,
        "per_day_budget": budget / max(days, 1),
        "destination_tier": tier,
        "travel_style": style,
    }])
    X = _featurize(row)
    X = X.reindex(columns=MODEL_BUNDLE["feature_columns"], fill_value=0)
    pred = MODEL_BUNDLE["pipeline"].predict(X)[0]
    return max(0, round(pred))


def build_budget_breakdown(remaining_budget, style):
    split = BUDGET_SPLIT.get(style, BUDGET_SPLIT["relaxed"])
    return {
        category: round(remaining_budget * pct)
        for category, pct in split.items()
    }


def build_itinerary(destination_key, days, tier, style):
    pool = ACTIVITY_POOL.get(tier, ACTIVITY_POOL["tier2"])[style]
    themes = (
        [DAY_THEME_TEMPLATES[0]]
        + DAY_THEME_TEMPLATES[1:-1]
        + [DAY_THEME_TEMPLATES[-1]]
    )

    itinerary = []
    used = set()
    for day_num in range(1, days + 1):
        if day_num == 1:
            theme = "Arrival & First Impressions"
        elif day_num == days and days > 1:
            theme = "Departure Day"
        else:
            mid_themes = [t for t in themes if t not in ("Arrival & First Impressions", "Departure Day")]
            theme = mid_themes[(day_num - 2) % len(mid_themes)]

        available = [a for a in pool if a not in used] or list(pool)
        picks = random.sample(available, k=min(2, len(available)))
        used.update(picks)

        if day_num == 1:
            morning = "Check-in and settle into your stay"
            afternoon = picks[0] if picks else "Explore the neighbourhood on foot"
            evening = "An easy dinner near your stay to beat jet lag"
        elif day_num == days and days > 1:
            morning = picks[0] if picks else "Last-minute local shopping"
            afternoon = "Pack up and check out"
            evening = "Head to the airport / station"
        else:
            morning = picks[0] if picks else "Free exploration"
            afternoon = picks[1] if len(picks) > 1 else "Rest and recharge"
            evening = "Dinner at a locally recommended spot"

        itinerary.append({
            "day": day_num,
            "theme": theme,
            "morning": morning,
            "afternoon": afternoon,
            "evening": evening,
        })

    return itinerary


@app.route("/")
def home():
    destinations_json = json.dumps({
        key: {"label": d["label"], "state": d["state"]}
        for key, d in DESTINATIONS.items()
    })
    return render_template(
        "index.html",
        destinations=DESTINATIONS,
        destinations_json=destinations_json,
        travel_modes=TRAVEL_MODES,
    )


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user_id"):
        return redirect(url_for("home"))

    if request.method == "GET":
        return render_template("signup.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")

    error = None
    if not name:
        error = "Please enter your name."
    elif not EMAIL_RE.match(email):
        error = "Please enter a valid email address."
    elif len(password) < 6:
        error = "Password should be at least 6 characters."
    elif password != confirm:
        error = "Passwords don't match."

    if error:
        return render_template("signup.html", error=error, name=name, email=email), 400

    ok, err = auth_db.create_user(name, email, password)
    if not ok:
        return render_template("signup.html", error=err, name=name, email=email), 400

    user = auth_db.get_user_by_email(email)
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    flash(f"Welcome to TripGenius, {user['name']}!")
    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("home"))

    if request.method == "GET":
        return render_template("login.html", next_url=request.args.get("next", ""))

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    next_url = request.form.get("next", "") or url_for("home")

    user = auth_db.verify_user(email, password)
    if not user:
        return render_template(
            "login.html", error="Incorrect email or password.", email=email, next_url=next_url
        ), 400

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    flash(f"Welcome back, {user['name']}!")
    return redirect(next_url or url_for("home"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You've been logged out.")
    return redirect(url_for("home"))


@app.route("/api/plan", methods=["POST"])
@login_required
def api_plan():
    data = request.get_json(force=True) or {}

    # ---- basic field parsing ------------------------------------------------
    try:
        budget = int(data.get("budget", 0))
        days = int(data.get("days", 0))
        destination_key = str(data.get("destination", "")).strip().lower()
        style = str(data.get("style", "relaxed")).strip().lower()
        travel_mode = str(data.get("travel_mode", "car")).strip().lower()
        source_key = str(data.get("source_key", "")).strip().lower()
        source_lat = data.get("source_lat")
        source_lon = data.get("source_lon")
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input types."}), 400

    if budget < 1000:
        return jsonify({"error": "Budget should be at least Rs.1,000."}), 400
    if not (1 <= days <= 21):
        return jsonify({"error": "Days should be between 1 and 21."}), 400
    if destination_key not in DESTINATIONS:
        return jsonify({"error": "Please choose a supported destination from the search."}), 400
    if style not in BUDGET_SPLIT:
        style = "relaxed"
    if travel_mode not in TRAVEL_MODES:
        return jsonify({"error": "Please choose a valid mode of travel."}), 400

    # ---- resolve the traveller's starting point ------------------------------
    # Either a picked city (source_key, looked up in the same destinations
    # dataset) or raw GPS coordinates from the browser's location API.
    if source_key and source_key in DESTINATIONS:
        src = DESTINATIONS[source_key]
        src_lat, src_lon = src["lat"], src["lon"]
        source_label = src["label"]
    elif source_lat is not None and source_lon is not None:
        try:
            src_lat, src_lon = float(source_lat), float(source_lon)
        except (TypeError, ValueError):
            return jsonify({"error": "Could not read your location. Please search your city instead."}), 400
        if not (-90 <= src_lat <= 90 and -180 <= src_lon <= 180):
            return jsonify({"error": "That location looks invalid. Please search your city instead."}), 400
        source_label = "your current location"
    else:
        return jsonify({"error": "Please share your starting location — use GPS or search your city."}), 400

    tier = DESTINATIONS[destination_key]["tier"]
    label = DESTINATIONS[destination_key]["label"]
    dest_lat, dest_lon = DESTINATIONS[destination_key]["lat"], DESTINATIONS[destination_key]["lon"]

    # ---- distance + intercity travel cost ------------------------------------
    one_way_km = estimate_road_distance_km(src_lat, src_lon, dest_lat, dest_lon)
    travel_cost, travel_detail = estimate_travel_cost(one_way_km, travel_mode)

    # ---- stay cost (ML model) + total required --------------------------------
    stay_cost = predict_estimated_cost(days, budget, tier, style)
    total_required = stay_cost + travel_cost

    # ---- feasibility check ------------------------------------------------------
    ratio = budget / total_required if total_required > 0 else 1.0
    if ratio < MIN_FEASIBLE_RATIO:
        return jsonify({
            "error": (
                f"Your budget of Rs.{budget:,} is too low for this trip. "
                f"A {days}-day {style} trip to {label} by {TRAVEL_MODES[travel_mode]['label'].lower()} "
                f"typically needs at least Rs.{total_required:,} "
                f"(Rs.{travel_cost:,} travel + Rs.{stay_cost:,} stay). "
                f"Try a closer destination, fewer days, or a cheaper travel mode."
            ),
            "min_required": total_required,
        }), 400

    if ratio >= SURPLUS_RATIO:
        budget_status = "surplus"
    elif ratio >= 1.0:
        budget_status = "comfortable"
    else:
        budget_status = "shortfall"

    remaining_after_travel = max(budget - travel_cost, 0)
    breakdown = build_budget_breakdown(remaining_after_travel, style)
    breakdown_with_travel = {"intercity_travel": travel_cost, **breakdown}

    itinerary = build_itinerary(destination_key, days, tier, style)
    dest_info = DESTINATIONS[destination_key]
    image_url = get_destination_image_url(destination_key, dest_info)

    # ---- tips ------------------------------------------------------------------
    tips = []
    if budget_status == "surplus":
        tips.append(
            f"You have solid surplus room — about Rs.{budget - total_required:,} more than a "
            f"{style} trip to {label} typically needs. Consider a nicer hotel tier or an extra activity."
        )
    elif budget_status == "comfortable":
        tips.append(
            f"Your budget comfortably covers this trip, with about Rs.{budget - total_required:,} to spare."
        )
    else:
        shortfall = total_required - budget
        tips.append(
            f"This trip is tight — you're about Rs.{shortfall:,} short of the typical Rs.{total_required:,} "
            f"needed. Consider a cheaper travel mode, one fewer day, or a lower hotel tier."
        )
    tips.append(f"Travel estimate: {travel_detail} by {TRAVEL_MODES[travel_mode]['label'].lower()} — {TRAVEL_MODES[travel_mode]['note']}")
    tips.append("Book transport and hotels 2-3 weeks ahead for the best local prices.")

    return jsonify({
        "destination": label,
        "destination_state": dest_info["state"],
        "days": days,
        "style": style,
        "budget": budget,
        "source_label": source_label,
        "travel_mode": TRAVEL_MODES[travel_mode]["label"],
        "distance_km": round(one_way_km),
        "travel_cost": travel_cost,
        "travel_detail": travel_detail,
        "stay_cost": stay_cost,
        "total_required": total_required,
        "budget_status": budget_status,
        "budget_breakdown": breakdown_with_travel,
        "itinerary": itinerary,
        "famous_food": dest_info["food"],
        "famous_things": dest_info["things"],
        "image_url": image_url,
        "tips": tips,
        "model_metrics": MODEL_BUNDLE["metrics"],
    })


if __name__ == "__main__":
    app.run(debug=True)
