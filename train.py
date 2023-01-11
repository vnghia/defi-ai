import os

import pandas as pd
from catboost import CatBoostRegressor, Pool

os.environ["HOST_URL"] = "http://51.91.251.0:3000"
os.environ["USER_ID"] = "f89fec0b-183b-4921-bf15-197101c14192"
os.environ["SQL_USERNAME"] = "postgres"
os.environ["SQL_PASSWORD"] = "^de<@TETh~}*;:/*"
os.environ["SQL_HOST"] = "34.155.175.170"
os.environ["SQL_PORT"] = "5432"
os.environ["SQL_SCRAPE_DATABASE"] = "scrape"

from defi_ai import Request, Sample, init_session

Session = init_session()
session = Session()


df_x, df_y = Request.load_dataset(session)
sample = Sample.load_dataset(session)

df_y_stock = pd.concat([df_x[["stock"]], sample[["stock"]]])
df_x_stock = pd.concat([df_x.drop(columns="stock"), sample.drop(columns="stock")])

price_dataset = Pool(
    data=df_x,
    label=df_y,
    cat_features=["language", "city", "group", "brand", "children_policy", "hotel_id"],
)

price_model = CatBoostRegressor(iterations=20000, random_state=42, task_type="GPU")

price_model.fit(price_dataset, metric_period=1000)
price_model.save_model("model/price_catboost.cbm", pool=price_dataset)

stock_dataset = Pool(
    data=df_x_stock,
    label=df_y_stock,
    cat_features=["language", "city", "group", "brand", "children_policy", "hotel_id"],
)

stock_model = CatBoostRegressor(iterations=20000, random_state=42, task_type="GPU")

stock_model.fit(stock_dataset, metric_period=1000)
stock_model.save_model("model/stock_catboost.cbm", pool=stock_dataset)
