# TripGenius — AI Travel Planner

An internship project (Data Science & AI/ML using Python) that plans a
budget-aware, day-by-day trip from three inputs: **destination, days, budget**.

## AI-generated destination image

Every plan now includes an **AI-generated preview image** of the
destination (`images.py`), using Pollinations.ai's free text-to-image
endpoint — no API key required. A descriptive prompt is built from the
destination's name, state, and top attraction (e.g. *"Agra, Uttar Pradesh,
India, Taj Mahal, travel photography, golden hour lighting..."*), and the
resulting URL is set directly as an `<img src="...">` — the browser
requests the image straight from Pollinations, so no image bytes pass
through the Flask server. A fixed per-destination seed keeps the same
place returning a consistent image across visits instead of a new random
one every time.

## What's new: destinations, location, and travel cost

- **48 Indian destinations** spanning metro cities, tier-2 cities, hill
  stations, beaches, and heritage towns (`data/knowledge_base.py`) — each
  with real coordinates, famous food, and must-see attractions. The
  destination field is a live **search box**, not a fixed dropdown.
- **Starting location**: either tap **"Use my current location"** (browser
  GPS via `navigator.geolocation` — works for any city or village, no API
  key needed) or search a starting city from the same destinations dataset.
- **Distance-based travel cost** (`travel.py`): a haversine great-circle
  distance between source and destination, scaled by a road-distance factor,
  then converted into a round-trip cost for **Car, Bike, Bus, or Train** —
  each with its own transparent assumption (fuel price & mileage, or
  per-km fare), shown to the user alongside the number.
- **Smart budget verdicts**: the total required cost = ML-predicted stay
  cost + computed travel cost. Depending on how the user's budget compares:
  - **Surplus** — budget comfortably exceeds what's needed (suggests upgrades)
  - **Comfortable** — within budget with some headroom
  - **Shortfall** — feasible but tight, with the exact shortfall shown
  - **Rejected outright** (HTTP 400, clear error) if the budget is far too
    low for the destination/days/travel mode combination — no itinerary is
    generated in that case, since it wouldn't be realistic.

## What's "AI/ML" about it

1. **Trained cost-prediction model** (`model/train_model.py`)
   A scikit-learn `LinearRegression` pipeline (with `StandardScaler`) trained
   on a synthetic-but-domain-realistic dataset of trips, engineered from
   destination cost-tier, travel style, trip length, and budget. It predicts
   a realistic **estimated total spend**, which the app compares against the
   traveller's stated budget. Metrics (MAE, R²) are computed on a held-out
   test split and shown live in the UI so the model's honesty is visible,
   not hidden.

2. **Rule-based recommendation engine** (`data/knowledge_base.py` +
   `app.py: build_itinerary`, `build_budget_breakdown`)
   A curated content model (destinations → cost tier → activity pool) drives
   itinerary generation and the hotel/food/transport/activities budget split —
   a transparent, explainable recommender, appropriate to present and defend
   in a viva.

Both pieces are real, working Python — nothing is faked or hardcoded per
destination; change the model's training data or the activity pool and the
output changes accordingly.

## Login / signup

The planner is behind a simple account system:

- `auth_db.py` — SQLite storage (`tripgenius.db`, created automatically on
  first run) with hashed passwords (`werkzeug.security`), no plaintext ever stored.
- `/signup`, `/login`, `/logout` routes in `app.py`, using Flask's signed
  session cookie to keep you logged in.
- `/api/plan` is protected with a `@login_required` decorator — calling it
  while logged out returns `401` and the frontend redirects to `/login`.
- The header shows **Log in / Sign up** when signed out, and your first
  name + a **Log out** button when signed in.

Before deploying this anywhere public, set a real secret key:
```bash
export TRIPGENIUS_SECRET_KEY="a-long-random-string"
```
(otherwise it falls back to a fixed dev key, which is fine for local demos
but not for production.)

## Project structure

```
tripgenius/
├── app.py                     # Flask app, routes, API
├── auth_db.py                 # SQLite user storage (signup/login)
├── travel.py                  # distance calculation + travel-mode cost estimation
├── images.py                  # AI destination image URL generation (Pollinations.ai)
├── requirements.txt
├── model/
│   ├── train_model.py         # trains & saves the regression model
│   └── trip_cost_model.pkl    # generated on first run (git-ignoreable)
├── data/
│   └── knowledge_base.py      # 48 destinations, activities, budget-split rules
├── templates/
│   ├── index.html
│   ├── login.html
│   └── signup.html
└── static/
    ├── css/style.css
    └── js/main.js
```

## Run it locally

```bash
cd tripgenius
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://127.0.0.1:5000** — the model trains automatically on first run
(takes under a second) and is cached to `model/trip_cost_model.pkl` after that.

To retrain manually:
```bash
python model/train_model.py
```

## Demoing / for your report

- Fill the form (destination, days, budget, style) and click **Plan my trip**.
- The results panel shows: the model's cost estimate vs. your budget, a
  category-wise budget split, a full day-by-day itinerary, and notes.
- **Save as PDF** uses the browser's print dialog (`window.print()`) with a
  dedicated print stylesheet — no extra library needed.
- The `model_metrics` (MAE, R²) returned by `/api/plan` are worth screenshotting
  for your report as evidence of a trained, evaluated model rather than a
  lookup table.

## Extending it (good "future scope" talking points)

- Swap the synthetic training data for real scraped/booking data.
- Add more destinations to `data/knowledge_base.py` — no code changes needed
  elsewhere as long as the destination has a `tier`.
- Replace `LinearRegression` with a `RandomForestRegressor` or `XGBoost` model
  and compare metrics — the pipeline structure already supports it.
- Add a weather/price-alerts service (stubbed in the landing page today).

## Notes

- All costs are indicative model estimates, not live prices — the UI states
  this explicitly, which is worth keeping for academic honesty.
- No external API keys or internet access are required to run this project.
