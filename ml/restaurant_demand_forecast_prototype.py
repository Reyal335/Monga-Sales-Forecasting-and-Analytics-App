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

# In[1]:


import pandas as pd 
from sqlalchemy import create_engine
import numpy as np


# In[2]:


import datetime


# In[3]:


USER = 'postgres'
PASSWORD = 'Anyasam101'
HOST = 'Localhost'
PORT = '5432'
DB_NAME = 'MONGA'

connection_string = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
engine = create_engine(connection_string)

query = """
SELECT 
    c.calendar_date,
    o.store_id,
    mi.item_id,
    mi.category,
    mi.item_name,
    COALESCE(SUM(oi.quantity), 0) AS quantity
FROM calendar_dim c
CROSS JOIN menu_items mi
LEFT JOIN orders o ON o.order_timestamp::date = c.calendar_date
LEFT JOIN order_items oi ON oi.order_id = o.order_id AND oi.item_id = mi.item_id
WHERE mi.item_id NOT LIKE 'M%%'
GROUP BY c.calendar_date, o.store_id, mi.item_id, mi.item_name
ORDER BY mi.item_id, c.calendar_date;
"""


# In[4]:


try:
    df = pd.read_sql(query, con=engine)
    print(f"Successfully loaded {len(df)} rows.")

    # index=False prevents pandas from writing a row-number column into the CSV
    output_file = "data/extracted_data.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Data successfully saved to {output_file}")
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # 6. Dispose of the engine connection pool
    engine.dispose()


# In[5]:


items = df[~df['item_id'].str.contains('M')][['item_id', 'item_name']]
item_ids = items.drop_duplicates(subset=['item_id'], keep='first')

item_dict = df.set_index('item_name')['item_id'].to_dict()

def id_correction(row):
    return item_dict[row['item_name']]

df['item_id'] = df.apply(id_correction, axis=1)

df.to_csv('data/cleaned_extracted_data.csv', index=False)


# In[64]:


df.head()


# ### Engineering features
# 

# In[6]:


# Convert to datetime
df['calendar_date'] = pd.to_datetime(df['calendar_date'])
df['date'] = df['calendar_date'].dt.date
# Group by item to create time-series window features
grouped = df.groupby(['store_id', 'item_id'])['quantity']

df['lag_1'] = grouped.shift(1)
df['lag_7'] = grouped.shift(7).fillna(0)
df['lag_14'] = grouped.shift(14).fillna(0)
df['rolling_mean_7'] = grouped.transform(lambda x: x.rolling(7, min_periods=1).mean()).round(2)

# Date Features
df['day_of_week'] = df['calendar_date'].dt.dayofweek + 1  # 1=Mon, 7=Sun (ISODOW)
df['month'] = df['calendar_date'].dt.month
df['is_weekend'] = df['calendar_date'].dt.dayofweek.isin([5, 6]).astype(int)
df['is_payday'] = df['calendar_date'].dt.day.isin([15, 30, 31]).astype(int)

df = df.replace(np.nan, 0)
df.head()


# ### I realized seedfast created duplicate items with different ids, so I'll now try to map every item with the corresponing proper id 'SKU-x'

# ### Training the lightgbm model

# In[7]:


import lightgbm as lgb

cutoff_date = datetime.date(2026, 7, 1)
df["item_id"] = df["item_id"].astype("category")
df["store_id"] = df["store_id"].astype("category")
df["category"] = df["category"].astype("category")

FEATURES = ["item_id", "store_id", "category", "day_of_week", "is_weekend", "month",
            "lag_1", "lag_7", "lag_14", "rolling_mean_7", "is_payday"]
TARGET = "quantity"

cutoff_date = df["date"].max() - pd.Timedelta(days=21)
train = df[df["date"] <= cutoff_date]
test = df[df["date"] > cutoff_date].copy()

train_set = lgb.Dataset(train[FEATURES], label=train[TARGET], categorical_feature=["item_id", "store_id", "category"])
params = {"objective": "regression", "metric": "mae", "learning_rate": 0.05, "num_leaves": 31, "verbose": -1}
model = lgb.train(params, train_set, num_boost_round=300)


# ### Evaluation

# In[8]:


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


# ### Plot actual vs predicted

# In[9]:


import matplotlib.pyplot as plt

item = "The King"  # try swapping this for any item_name in the menu
sub = test[test["item_name"] == item].sort_values("date")

plt.figure(figsize=(9, 4.5))
plt.plot(sub["date"], sub["quantity"], label="Actual", marker="o", markersize=3)
plt.plot(sub["date"], sub["predicted"], label="Predicted", linestyle="--", marker="o", markersize=3)
plt.title(f"{item} — actual vs predicted daily units (test period)")
plt.xlabel("Date"); plt.ylabel("Units sold"); plt.legend(); plt.tight_layout()
plt.show()


# In[56]:


rn = 60
rm = rn + 5

actual_value = test.loc[test.index[rn:rm]]['quantity']
# # df.loc[0, FEATURES]
actual_value
predicted_value = model.predict(test.loc[test.index[[rn]], FEATURES])
# print(test.loc[test.index[[rn]], FEATURES])
print(f'Actual Value: \n{actual_value}')
print(f'Predicted Value: {predicted_value}')

# test.loc[[test.index[0]], FEATURES]


# ## Function to make a forecast of the quantity for an item, or eventually for each item ;)

# In[11]:


df.head()


# In[12]:


df[df['item_name'] == 'The King'].iloc[0]


# In[13]:


df[(df['item_name'] == 'The King') & (df['store_id'] == 'STR_02')]


# In[49]:


df['category'].cat.categories


# ## Function to calculate the predicted demand of each item per store using the model

# In[ ]:


lead_time = 28
stock_period = 60
forecast_duration = lead_time + stock_period
stock_date = df['calendar_date'].max()
cutoff_date = stock_date - pd.Timedelta(days=30)

def forecast_item(features):
    for col in ["item_id", "store_id", "category"]:
        features[col] = pd.Categorical(features[col], categories=df[col].cat.categories)
    predicted_qty = model.predict(features[FEATURES])
    return float(predicted_qty[0])

def add_dates(item_name, store_id):
    sim = df[(df['item_name'] == item_name) &
             (df['store_id'] == store_id) &
             (df['calendar_date'] >= cutoff_date)].reset_index(drop=True)

    item_data = df[df['item_name'] == item_name].iloc[0]
    item_id = item_data['item_id']
    category = item_data['category']
    latest_date = sim['calendar_date'].max()

    for i in range(forecast_duration):
        latest_date += pd.Timedelta(days=1)

        qty = sim['quantity']
        lag_1 = qty.iloc[-1]
        lag_7 = qty.iloc[-7] if len(qty) >= 7 else np.nan
        lag_14 = qty.iloc[-14] if len(qty) >= 14 else np.nan
        rolling_mean_7 = np.round(qty.tail(7).mean(), 2)

        day_of_week = latest_date.isoweekday()
        is_weekend = 1 if day_of_week in [6, 7] else 0
        is_payday = 1 if latest_date.day in [15, 30, 31] else 0

        features = pd.DataFrame([{
            'lag_1': lag_1, 'lag_7': lag_7, 'lag_14': lag_14,
            'rolling_mean_7': rolling_mean_7,
            'day_of_week': day_of_week, 'month': latest_date.month,
            'is_weekend': is_weekend, 'is_payday': is_payday,
            'category': category, 'item_id': item_id, 'store_id': store_id
        }])
        predicted_qty = forecast_item(features)

        new_row = pd.DataFrame([{
            'item_id': item_id, 'item_name': item_name,
            'calendar_date': latest_date, 'store_id': store_id,
            'category': category, 'date': latest_date.date(),
            'day_of_week': day_of_week, 'month': latest_date.month,
            'is_weekend': is_weekend, 'is_payday': is_payday,
            'lag_1': lag_1, 'lag_7': lag_7, 'lag_14': lag_14,
            'rolling_mean_7': rolling_mean_7,
            'quantity': predicted_qty,
        }])


        sim = pd.concat([sim, new_row], ignore_index=True)

    # Cutoff with no lead time
    predicted_total_ty = sim[sim['calendar_date'] >= stock_date]['quantity'].sum(axis=0)

    return predicted_total_ty

add_dates('The King', 'STR_01')

# test_df = df[(df['item_name'] == 'The King') & (df['store_id'] == 'STR_02') & (df['calendar_date'] >= cutoff_date)]


# ## Predicted amount of whole item, not taking into account yet ingredient and bill of materials

# In[63]:


print(f'Predicted The King demand for STR_01: {add_dates('The King', 'STR_01')}\n')
print(f'Predicted The King demand for STR_02: {add_dates('The King', 'STR_02')}\n')
print(f'Predicted The King demand for STR_03: {add_dates('The King', 'STR_03')}\n')
print(f'Predicted The King demand for STR_04: {add_dates('The King', 'STR_04')}')

