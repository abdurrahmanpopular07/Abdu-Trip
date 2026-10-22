"""
TripGenius — Cost Prediction Model
-----------------------------------
Trains a small regression model that predicts a realistic *estimated total
trip cost*, based on:
    - number of days
    - destination cost tier (metro / tier-2 / hill / beach / heritage)
    - travel style (relaxed / active / family)
    - the traveller's declared budget (used only as a weak signal, see note)

IMPORTANT DESIGN NOTE — why the target does NOT scale off the user's budget:
An earlier version of this model set target_cost = user_budget * ratio.
That made the "prediction" mathematically just a scaled copy of whatever
the user typed in, and since the average ratio across tiers/styles was
just above 1.0, the estimate came out higher than the budget almost every
single time — regardless of destination or trip length. That is a modeling
bug, not a real result: a genuine cost estimate must be anchored to what a
destination/style/length actually costs, not to the number the user
happened to type into the budget box.

This version anchors the target to fixed, hand-set INR per-day baseline
costs per destination tier and travel style (domain assumptions standing
in for real historical booking data). The user's budget is still passed in
as a feature so the pipeline/API shape is unchanged, but it no longer
drives the target's scale — so "within budget" vs "over budget" now
reflects a genuine comparison instead of a near-guaranteed overshoot.

This is intentionally a transparent, explainable model (Linear Regression
on engineered features) rather than a black box — appropriate for an
internship-level Data Science / ML demo, and fast enough to retrain on
every server start with no external dataset needed.

Run directly to (re)generate model/trip_cost_model.pkl:
    python model/train_model.py
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

RANDOM_SEED = 42

# Destination cost tiers: baseline INR cost per day (hotel + food + local
# transport + activities combined, mid-range travel), independent of budget.
DESTINATION_TIERS = {
    "metro":       4500,   # Mumbai, Delhi, Bengaluru
    "tier2":       3000,   # Jaipur, Lucknow, Indore
    "hill":        3200,   # Manali, Munnar, Darjeeling
    "beach":       3800,   # Goa, Pondicherry, Andaman
    "heritage":    2800,   # Agra, Hampi, Varanasi
}

# Travel style multiplier applied to the daily baseline above.
STYLE_MULTIPLIER = {
    "relaxed": 1.00,
    "active":  1.15,   # adventure add-ons, more local transport
    "family":  1.35,   # more people, more tickets, bigger rooms
}


def _synthesize_dataset(n=4000, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)

    days = rng.integers(1, 15, size=n)
    budget = rng.integers(3000, 200000, size=n)  # INR total trip budget (feature only)
    tiers = rng.choice(list(DESTINATION_TIERS.keys()), size=n)
    styles = rng.choice(list(STYLE_MULTIPLIER.keys()), size=n)

    rows = []
    for d, b, t, s in zip(days, budget, tiers, styles):
        per_day_budget = b / d
        base_daily_cost = DESTINATION_TIERS[t] * STYLE_MULTIPLIER[s]

        # Longer trips get a small per-day discount (multi-night hotel
        # deals, bulk transport passes), plus realistic noise (+/- ~8%).
        length_decay = 1.0 / (1.0 + 0.02 * d)
        noise_factor = 1.0 + rng.normal(0, 0.08)

        actual_daily_cost = max(500, base_daily_cost * length_decay * noise_factor)
        predicted_total_spend = actual_daily_cost * d

        rows.append({
            "days": d,
            "budget": b,
            "per_day_budget": per_day_budget,
            "destination_tier": t,
            "travel_style": s,
            "target_estimated_cost": predicted_total_spend,
        })

    return pd.DataFrame(rows)


def _featurize(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for tier in DESTINATION_TIERS:
        out[f"tier_{tier}"] = (out["destination_tier"] == tier).astype(int)
    for style in STYLE_MULTIPLIER:
        out[f"style_{style}"] = (out["travel_style"] == style).astype(int)
    feature_cols = (
        ["days", "budget", "per_day_budget"]
        + [f"tier_{t}" for t in DESTINATION_TIERS]
        + [f"style_{s}" for s in STYLE_MULTIPLIER]
    )
    return out[feature_cols]


def train_and_save(model_path=None):
    df = _synthesize_dataset()
    X = _featurize(df)
    y = df["target_estimated_cost"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("regressor", LinearRegression()),
    ])
    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    print(f"[TripGenius model] Test MAE: Rs.{mae:,.0f}  |  R2: {r2:.3f}")

    if model_path is None:
        model_path = os.path.join(os.path.dirname(__file__), "trip_cost_model.pkl")

    with open(model_path, "wb") as f:
        pickle.dump({
            "pipeline": pipeline,
            "feature_columns": list(X.columns),
            "destination_tiers": list(DESTINATION_TIERS.keys()),
            "travel_styles": list(STYLE_MULTIPLIER.keys()),
            "metrics": {"mae": mae, "r2": r2},
        }, f)

    print(f"[TripGenius model] Saved to {model_path}")
    return model_path


if __name__ == "__main__":
    train_and_save()

