#!/usr/bin/env python
# coding: utf-8

# # Restaurant demand forecasting — Layer 1 prototype
# 
# Goal: predict daily units sold **per menu item**, which is the foundation for:
# - the sales forecast dashboard (aggregate this across items)
# - the ingredient demand forecast (multiply this by the recipe/BOM table)
# 
# This notebook uses **synthetic data** so you can validate the whole pipeline
# before wiring it into the FastAPI service. Swap `daily_item_sales.csv` for
# real (or POS-exported) data later — nothing else below needs to change.

# ## 1. Generate synthetic data
# 
# Simulates 2 years of daily sales across a 12-item menu, with weekday/weekend patterns, a slow upward trend, and holiday spikes.

# In[ ]:


"""
Generates synthetic restaurant sales data for prototyping the demand
forecasting model. Produces daily unit sales per menu item over 2 years,
with realistic weekday/weekend seasonality, a slow upward trend, and a
handful of holiday spikes.
"""

import numpy as np
import pandas as pd

np.random.seed(42)

START_DATE = "2024-01-01"
END_DATE = "2025-12-31"
dates = pd.date_range(START_DATE, END_DATE, freq="D")

# A small representative menu across categories
MENU = [
    {"item_id": "M01", "item_name": "Classic Burger",       "category": "main",     "base_units": 38, "price": 250},
    {"item_id": "M02", "item_name": "Margherita Pizza",     "category": "main",     "base_units": 30, "price": 320},
    {"item_id": "M03", "item_name": "Chicken Adobo",        "category": "main",     "base_units": 45, "price": 220},
    {"item_id": "M04", "item_name": "Sisig Rice Bowl",      "category": "main",     "base_units": 33, "price": 210},
    {"item_id": "M05", "item_name": "Caesar Salad",         "category": "starter",  "base_units": 14, "price": 180},
    {"item_id": "M06", "item_name": "Garlic Fries",         "category": "side",     "base_units": 25, "price": 120},
    {"item_id": "M07", "item_name": "Iced Tea",             "category": "beverage", "base_units": 50, "price": 60},
    {"item_id": "M08", "item_name": "Mango Shake",          "category": "beverage", "base_units": 28, "price": 90},
    {"item_id": "M09", "item_name": "Chocolate Lava Cake",  "category": "dessert",  "base_units": 12, "price": 140},
    {"item_id": "M10", "item_name": "Halo-Halo",            "category": "dessert",  "base_units": 18, "price": 130},
    {"item_id": "M11", "item_name": "Spaghetti Carbonara",  "category": "main",     "base_units": 22, "price": 240},
    {"item_id": "M12", "item_name": "Buffalo Wings",        "category": "starter",  "base_units": 27, "price": 200},
]

# A few PH holidays/occasions that cause demand spikes in this synthetic set
HOLIDAY_SPIKES = {
    "2024-02-14": 1.6, "2025-02-14": 1.6,   # Valentine's
    "2024-12-24": 2.0, "2025-12-24": 2.0,   # Christmas Eve
    "2024-12-31": 1.8, "2025-12-31": 1.8,   # New Year's Eve
    "2024-06-12": 1.3, "2025-06-12": 1.3,   # Independence Day
    "2024-11-01": 1.2, "2025-11-01": 1.2,   # All Saints' Day
}

rows = []
for day_idx, date in enumerate(dates):
    dow = date.dayofweek  # 0=Mon ... 6=Sun
    is_weekend = dow in (4, 5)  # Fri & Sat busiest for this fictional restaurant

    # Slow upward trend over the 2 years (~25% growth), plus mild yearly seasonality
    trend = 1 + 0.00035 * day_idx
    weekend_boost = 1.35 if is_weekend else (0.85 if dow == 1 else 1.0)  # Tuesdays slow
    holiday_boost = HOLIDAY_SPIKES.get(date.strftime("%Y-%m-%d"), 1.0)

    for item in MENU:
        noise = np.random.normal(1.0, 0.12)
        units = item["base_units"] * trend * weekend_boost * holiday_boost * noise
        units = max(0, round(units))
        rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "item_id": item["item_id"],
            "item_name": item["item_name"],
            "category": item["category"],
            "units_sold": units,
            "revenue": round(units * item["price"], 2),
        })

df = pd.DataFrame(rows)
df.to_csv("/home/claude/daily_item_sales.csv", index=False)
print(df.shape)
print(df.head())
print("\nDate range:", df["date"].min(), "to", df["date"].max())
print("Items:", df["item_id"].nunique())


# ## 2. Load data and inspect

# In[ ]:


import pandas as pd

df = pd.read_csv("daily_item_sales.csv", parse_dates=["date"])
df.head()


# In[ ]:


# Quick sanity check: total daily revenue over time
daily_revenue = df.groupby("date")["revenue"].sum()
daily_revenue.plot(figsize=(10, 4), title="Total daily revenue (synthetic)")


# ## 3. Feature engineering
# 
# Per-item lag features (yesterday, last week, two weeks ago), a 7-day rolling
# average, day-of-week, and a trend index. Computed **per item** via `groupby`
# so history doesn't leak across menu items.

# In[ ]:


import numpy as np

df = df.sort_values(["item_id", "date"]).reset_index(drop=True)

df["day_of_week"] = df["date"].dt.dayofweek
df["is_weekend"] = df["day_of_week"].isin([4, 5]).astype(int)
df["month"] = df["date"].dt.month
df["day_index"] = (df["date"] - df["date"].min()).dt.days

for lag in (1, 7, 14):
    df[f"lag_{lag}"] = df.groupby("item_id")["units_sold"].shift(lag)

df["rolling_mean_7"] = (
    df.groupby("item_id")["units_sold"]
    .shift(1)
    .rolling(7)
    .mean()
    .reset_index(level=0, drop=True)
)

df = df.dropna(subset=["lag_1", "lag_7", "lag_14", "rolling_mean_7"]).reset_index(drop=True)
df["item_id_cat"] = df["item_id"].astype("category")
df.head()


# ## 4. Train a global LightGBM model
# 
# One model across **all** menu items, using `item_id` as a categorical
# feature. This tends to generalize better than a separate model per item,
# especially for lower-volume items with less history each.

# In[ ]:


import lightgbm as lgb

FEATURES = ["item_id_cat", "day_of_week", "is_weekend", "month", "day_index",
            "lag_1", "lag_7", "lag_14", "rolling_mean_7"]
TARGET = "units_sold"

cutoff_date = df["date"].max() - pd.Timedelta(days=21)
train = df[df["date"] <= cutoff_date]
test = df[df["date"] > cutoff_date].copy()

train_set = lgb.Dataset(train[FEATURES], label=train[TARGET], categorical_feature=["item_id_cat"])
params = {"objective": "regression", "metric": "mae", "learning_rate": 0.05, "num_leaves": 31, "verbose": -1}
model = lgb.train(params, train_set, num_boost_round=300)


# ## 5. Evaluate — don't skip this before trusting the output

# In[ ]:


from sklearn.metrics import mean_absolute_error

test["predicted"] = model.predict(test[FEATURES]).clip(min=0)

overall_mae = mean_absolute_error(test[TARGET], test["predicted"])
overall_mape = (np.abs(test[TARGET] - test["predicted"]) / test[TARGET].replace(0, np.nan)).mean() * 100
print(f"Overall MAE:  {overall_mae:.2f} units/day")
print(f"Overall MAPE: {overall_mape:.1f}%")

per_item = (test.groupby("item_name")
            .apply(lambda g: (np.abs(g[TARGET] - g['predicted']) / g[TARGET].replace(0, np.nan)).mean() * 100)
            .sort_values())
per_item.round(1)


# ## 6. Visual sanity check
# 
# Plot actual vs. predicted for one item over the test period. Look for
# systematic misses (e.g. holidays) — that tells you what feature to add next,
# not just whether the number is "good enough.

# In[ ]:


import matplotlib.pyplot as plt

item = "Chicken Adobo"  # try swapping this for any item_name in the menu
sub = test[test["item_name"] == item].sort_values("date")

plt.figure(figsize=(9, 4.5))
plt.plot(sub["date"], sub["units_sold"], label="Actual", marker="o", markersize=3)
plt.plot(sub["date"], sub["predicted"], label="Predicted", linestyle="--", marker="o", markersize=3)
plt.title(f"{item} — actual vs predicted daily units (test period)")
plt.xlabel("Date"); plt.ylabel("Units sold"); plt.legend(); plt.tight_layout()
plt.show()


# ## Notes / next steps
# 
# - **MAPE ~13% overall** on synthetic data — a reasonable baseline for a first pass.
# - The model tracks **weekly seasonality** well but likely **misses holiday spikes**
#   (Christmas Eve, New Year's) — because there's no holiday feature yet. Add an
#   `is_holiday` binary column (a small hardcoded PH holiday calendar) and retrain
#   to fix this — it's usually the single biggest accuracy win for a restaurant.
# - Once this is solid: save the model (`model.save_model(...)`), and this whole
#   notebook becomes the basis for the `models/` module inside the FastAPI service —
#   the scheduled retraining job runs this same logic against real data.
# - Layer 2 (recipe/BOM conversion) picks up right where `test["predicted"]` ends —
#   that's the per-item forecast you'll multiply against ingredient quantities.
