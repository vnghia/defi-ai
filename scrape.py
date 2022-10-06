import os
from datetime import date
from posixpath import join as urljoin

import pandas as pd
import requests

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
