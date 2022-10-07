import os
from datetime import date
from posixpath import join as urljoin

import pandas as pd
import requests

from req_enums import City, Language

HOST_URL = os.environ["HOST_URL"]
USER_ID = os.environ["USER_ID"]
REQUEST_COUNT = os.environ["REQUEST_COUNT"]

request_count = pd.read_csv(REQUEST_COUNT, index_col="date", parse_dates=True)
today = pd.Timestamp(date.today())


def update_request_count():
    if today in request_count.index:
        request_count.loc[today, "count"] += 1
    else:
        request_count.loc[today, "count"] = 1
    request_count.to_csv(REQUEST_COUNT)


def get_url(*paths) -> str:
    return urljoin(HOST_URL, *paths)


def create_user(name: str) -> tuple[int, str]:
    update_request_count()
    r = requests.post(get_url("avatars", USER_ID, name))
    r.raise_for_status()
    body = r.json()
    return body["id"], body["name"]


def list_users() -> list[tuple[int, str]]:
    update_request_count()
    r = requests.get(get_url("avatars", USER_ID))
    r.raise_for_status()
    body = r.json()
    return [(user["id"], user["name"]) for user in body]


def get_pricing(
    name: str,
    language: Language,
    city: City,
    date: int,
    mobile: bool,
) -> list[dict[str, int]]:
    update_request_count()
    params = {
        "avatar_name": name,
        "language": language.name,
        "city": city.name,
        "date": date,
        "mobile": int(mobile),
    }
    r = requests.get(get_url("pricing", USER_ID), params=params)
    r.raise_for_status()
    return r.json()["prices"]
