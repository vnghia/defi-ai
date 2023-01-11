import itertools
import os
import random
import string

import catboost
import gradio as gr

os.environ["HOST_URL"] = "http://51.91.251.0:3000"
os.environ["USER_ID"] = "f89fec0b-183b-4921-bf15-197101c14192"
os.environ["SQL_USERNAME"] = "postgres"
os.environ["SQL_PASSWORD"] = "^de<@TETh~}*;:/*"
os.environ["SQL_HOST"] = "34.155.175.170"
os.environ["SQL_PORT"] = "5432"
os.environ["SQL_SCRAPE_DATABASE"] = "scrape"

import functools

import pandas as pd
from sqlalchemy import select

from defi_ai import Hotel, init_session
from defi_ai.sql.utils import execute_to_df
from defi_ai.type import City, HotelBrand, Language

Session = init_session()
session = Session()

price_model = catboost.CatBoostRegressor()
price_model.load_model(fname="model/price_catboost.cbm")

stock_model = catboost.CatBoostRegressor()
stock_model.load_model(fname="model/stock_catboost.cbm")


def get_hotel_df(session):
    hotel_count_subq = Hotel.get_count_statement().subquery()
    statement = select(
        Hotel.id,
        Hotel.city,
        Hotel.group,
        Hotel.brand,
        Hotel.parking,
        Hotel.pool,
        Hotel.children_policy,
        hotel_count_subq.c.hotel_city_count,
        hotel_count_subq.c.hotel_brand_count,
        hotel_count_subq.c.hotel_group_count,
        hotel_count_subq.c.hotel_city_group_count,
        hotel_count_subq.c.hotel_city_brand_count,
    ).join(Hotel, hotel_count_subq.c.id == Hotel.id)
    return execute_to_df(session, statement, True, False)


hotel_df = get_hotel_df(session)


def get_random_string(length: int = 10):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def add_user(users: dict, name: str):
    users[name] = []
    return (
        users,
        get_random_string(),
        gr.Dropdown.update(choices=list(users.keys()), interactive=True),
    )


def login_user(users: dict, username: str):
    return (
        username,
        gr.Dropdown.update(interactive=True),
        gr.Dropdown.update(interactive=True),
        None,
        users[username],
    )


def get_hotel_list(hotel_df: pd.DataFrame, city: str, hotel_brand: str):
    hotels = hotel_df[
        (hotel_df.city == City[city.lower()])
        & (hotel_df.brand == HotelBrand[hotel_brand])
    ][["parking", "pool", "children_policy"]]
    return (
        gr.Dropdown.update(
            choices=[
                f"id {index} hotel {hotel_brand} city {city} parking {value[0]} pool {value[1]} children policy {value[2]}"
                for index, value in hotels.iterrows()
            ],
            interactive=True,
        ),
        gr.Dropdown.update(interactive=True),
        gr.Checkbox.update(interactive=True),
        gr.Slider.update(interactive=True),
    )


def get_price(
    price_model: catboost.CatBoostRegressor,
    stock_model: catboost.CatBoostRegressor,
    hotel_df: pd.DataFrame,
    users: dict,
    username: str,
    language: str,
    city: str,
    date: float,
    mobile: bool,
    hotel: str,
    stock: int,
):
    userdata = users[username]
    language = Language[language.lower()]
    city = City[city.lower()]
    date = int(date)
    hotel_id = int("".join(itertools.takewhile(str.isdigit, hotel[len("id ") :])))
    (
        group,
        brand,
        parking,
        pool,
        children_policy,
        hotel_city_count,
        hotel_brand_count,
        hotel_group_count,
        hotel_city_group_count,
        hotel_city_brand_count,
    ) = hotel_df[hotel_df.id == hotel_id][
        [
            "group",
            "brand",
            "parking",
            "pool",
            "children_policy",
            "hotel_city_count",
            "hotel_brand_count",
            "hotel_group_count",
            "hotel_city_group_count",
            "hotel_city_brand_count",
        ]
    ].values[
        0
    ]
    request_count = len(userdata) + 1
    request_language_count = 1
    request_city_count = 1
    request_date_count = 1
    request_mobile_count = 1
    for data in userdata:
        if data["language"] == language:
            request_language_count += 1
        if data["city"] == city:
            request_city_count += 1
        if data["date"] == date:
            request_date_count += 1
        if data["mobile"] == mobile:
            request_mobile_count += 1
    stock = int(
        stock
        if stock >= 0
        else stock_model.predict(
            [
                language,
                city,
                date,
                mobile,
                hotel_id,
                group,
                brand,
                parking,
                pool,
                children_policy,
                request_count,
                request_language_count,
                request_city_count,
                request_date_count,
                request_mobile_count,
                hotel_city_count,
                hotel_brand_count,
                hotel_group_count,
                hotel_city_group_count,
                hotel_city_brand_count,
            ]
        )
    )
    price = price_model.predict(
        [
            language,
            city,
            date,
            mobile,
            hotel_id,
            group,
            brand,
            parking,
            pool,
            children_policy,
            stock,
            request_count,
            request_language_count,
            request_city_count,
            request_date_count,
            request_mobile_count,
            hotel_city_count,
            hotel_brand_count,
            hotel_group_count,
            hotel_city_group_count,
            hotel_city_brand_count,
        ]
    )
    userdata.append(
        {
            "language": language,
            "city": city,
            "date": date,
            "mobile": mobile,
            "hotel_id": hotel_id,
            "price": price,
        }
    )
    return price, userdata


demo = gr.Blocks()

with demo:
    users = gr.State({})
    with gr.Column():
        signup_username = gr.Text(
            value=get_random_string(),
            label="Signup username",
        )
        signup_btn = gr.Button("Signup")
        usernames = gr.Dropdown([], label="Login username")
        signup_btn.click(
            add_user, [users, signup_username], [users, signup_username, usernames]
        )
        current_user = gr.Text(
            "Not login yet!", interactive=False, label="Current user"
        )
        login_btn = gr.Button("Login")

        with gr.Row():
            cities = gr.Dropdown(
                [e.name.capitalize() for e in City],
                label="City",
                interactive=False,
            )
            hotel_brands = gr.Dropdown(
                [e.name for e in HotelBrand],
                label="Hotel brand",
                interactive=False,
            )
        hotel_btn = gr.Button("Search hotels")
        hotels = gr.Dropdown([], label="Hotels")

        with gr.Row():
            with gr.Column():
                languages = gr.Dropdown(
                    [e.name.capitalize() for e in Language],
                    label="Language",
                    interactive=False,
                )
                stock = gr.Number(label="Stock")
            with gr.Column():
                is_mobile = gr.Checkbox(
                    label="Is mobile",
                    interactive=False,
                )
                date_before = gr.Slider(
                    0,
                    44,
                    step=1,
                    label="Date before",
                    interactive=False,
                )
        price_btn = gr.Button("Get Price")

        hotel_btn.click(
            functools.partial(get_hotel_list, hotel_df),
            [cities, hotel_brands],
            [hotels, languages, is_mobile, date_before],
        )

        price = gr.Text(label="Price")
        histories = gr.JSON(label="History")
        price_btn.click(
            functools.partial(get_price, price_model, stock_model, hotel_df),
            [
                users,
                usernames,
                languages,
                cities,
                date_before,
                is_mobile,
                hotels,
                stock,
            ],
            [price, histories],
        )

        login_btn.click(
            login_user,
            [users, usernames],
            [current_user, cities, hotel_brands, price, histories],
        )


if __name__ == "__main__":
    demo.launch(share=True)
