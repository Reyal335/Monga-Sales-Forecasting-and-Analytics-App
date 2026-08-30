from __future__ import annotations

from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "extracted_data.csv"
MODEL_PATH = BASE_DIR / "restaurant_demand_model.txt"
FEATURES = [
    "item_id",
    "store_id",
    "category",
    "day_of_week",
    "is_weekend",
    "month",
    "lag_1",
    "lag_7",
    "lag_14",
    "rolling_mean_7",
    "is_payday",
]
TARGET = "quantity"


@st.cache_data
def load_extracted_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Training data not found at {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    df["calendar_date"] = pd.to_datetime(df["calendar_date"])
    df["date"] = df["calendar_date"].dt.date

    grouped = df.groupby(["store_id", "item_id"])["quantity"]
    df["lag_1"] = grouped.shift(1).fillna(0)
    df["lag_7"] = grouped.shift(7).fillna(0)
    df["lag_14"] = grouped.shift(14).fillna(0)
    df["rolling_mean_7"] = grouped.transform(lambda x: x.rolling(7, min_periods=1).mean()).round(2)
    df["day_of_week"] = df["calendar_date"].dt.dayofweek + 1
    df["month"] = df["calendar_date"].dt.month
    df["is_weekend"] = df["calendar_date"].dt.dayofweek.isin([5, 6]).astype(int)
    df["is_payday"] = df["calendar_date"].dt.day.isin([15, 30, 31]).astype(int)
    df = df.replace({np.nan: 0})
    df["item_id"] = df["item_id"].astype("category")
    df["store_id"] = df["store_id"].astype("category")
    df["category"] = df["category"].astype("category")
    return df


@st.cache_resource
def load_or_train_model() -> lgb.Booster:
    df = load_extracted_data()

    if MODEL_PATH.exists():
        model = lgb.Booster(model_file=str(MODEL_PATH))
        return model

    cutoff_date = df["date"].max() - pd.Timedelta(days=21)
    train = df[df["date"] <= cutoff_date]

    train_set = lgb.Dataset(
        train[FEATURES],
        label=train[TARGET],
        categorical_feature=["item_id", "store_id", "category"],
    )
    params = {
        "objective": "regression",
        "metric": "mae",
        "learning_rate": 0.05,
        "num_leaves": 31,
        "verbose": -1,
    }
    model = lgb.train(params, train_set, num_boost_round=300)
    model.save_model(str(MODEL_PATH))
    return model


@st.cache_data
def build_history_for_item(df: pd.DataFrame, store_id: str, item_id: str) -> pd.DataFrame:
    subset = df[(df["store_id"] == store_id) & (df["item_id"] == item_id)]
    return subset.sort_values("calendar_date").reset_index(drop=True)


def make_prediction_row(df: pd.DataFrame, selected_date: pd.Timestamp, store_id: str, item_id: str) -> pd.DataFrame:
    item_history = build_history_for_item(df, store_id, item_id)
    category = item_history["category"].iloc[0]

    timestamp = pd.Timestamp(selected_date)
    past = item_history[item_history["calendar_date"] <= timestamp].copy()

    if past.empty:
        lag_1 = 0.0
        lag_7 = 0.0
        lag_14 = 0.0
        rolling_mean_7 = 0.0
    else:
        quantity = past["quantity"].astype(float)
        lag_1 = float(quantity.iloc[-1])
        lag_7 = float(quantity.iloc[-7]) if len(quantity) >= 7 else 0.0
        lag_14 = float(quantity.iloc[-14]) if len(quantity) >= 14 else 0.0
        rolling_mean_7 = float(quantity.tail(7).mean()) if len(quantity) >= 1 else 0.0

    row = pd.DataFrame(
        [{
            "item_id": item_id,
            "store_id": store_id,
            "category": category,
            "day_of_week": int(timestamp.dayofweek + 1),
            "is_weekend": int(timestamp.dayofweek in [5, 6]),
            "month": int(timestamp.month),
            "lag_1": lag_1,
            "lag_7": lag_7,
            "lag_14": lag_14,
            "rolling_mean_7": rolling_mean_7,
            "is_payday": int(timestamp.day in [15, 30, 31]),
        }]
    )

    for col in ["item_id", "store_id", "category"]:
        row[col] = row[col].astype("category")

    return row


st.set_page_config(page_title="Monga Demand Forecast", page_icon="🍽️", layout="wide")

st.title("Monga demand forecast")
st.caption("LightGBM forecast using lag, weekday, month, and rolling sales features.")

model = load_or_train_model()
df = load_extracted_data()

all_items = df[["item_name", "item_id", "category"]].drop_duplicates().sort_values("item_name")
store_options = sorted(df["store_id"].dropna().unique().tolist())
item_lookup = all_items.set_index("item_name")

with st.form("forecast_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_date = st.date_input("Forecast date", value=pd.Timestamp(df["date"].max()).date())
    with col2:
        selected_store = st.selectbox("Store", store_options)
    with col3:
        selected_item_name = st.selectbox("Menu item", item_lookup.index.tolist())

    submitted = st.form_submit_button("Predict")

if submitted:
    selected_item_id = item_lookup.loc[selected_item_name, "item_id"]
    row = make_prediction_row(df, pd.Timestamp(selected_date), selected_store, selected_item_id)
    prediction = float(model.predict(row[FEATURES])[0])

    history = build_history_for_item(df, selected_store, selected_item_id)
    history = history[history["calendar_date"] >= (pd.Timestamp(selected_date) - pd.Timedelta(days=30))]

    st.subheader("Forecast result")
    st.metric("Predicted units", f"{max(prediction, 0):.2f}")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Store: {selected_store}")
        st.write(f"Item: {selected_item_name}")
        st.write(f"Date: {selected_date}")
    with col2:
        st.write(f"Category: {item_lookup.loc[selected_item_name, 'category']}")
        st.write(f"Last observed value: {history['quantity'].tail(1).iloc[0] if not history.empty else 0}")

    st.subheader("Recent history")
    if not history.empty:
        chart_data = history[["calendar_date", "quantity"]].rename(columns={"calendar_date": "date", "quantity": "units"}).set_index("date")
        st.line_chart(chart_data)
    else:
        st.info("No historical sales available for this store/item combination yet.")

else:
    st.info("Choose a date, store, and item, then click Predict to estimate daily demand.")
