# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
from datetime import date
from posixpath import join as urljoin

import requests

from defi_ai.sql.model.request_count import RequestCount
from defi_ai.type import City, Language, SQLSession

HOST_URL = os.environ["HOST_URL"]
USER_ID = os.environ["USER_ID"]


def update_request_count(session: SQLSession):
    today = date.today()
    rc: RequestCount = session.get(RequestCount, today)
    if rc is None:
        session.add(RequestCount(date=today, count=1))
    else:
        rc.count += 1
    session.commit()


def get_url(*paths: str) -> str:
    return urljoin(HOST_URL, *paths)


def create_user(name: str) -> tuple[int, str]:
    r = requests.post(get_url("avatars", USER_ID, name))
    r.raise_for_status()
    body = r.json()
    return body["id"], body["name"]


def list_users() -> list[tuple[int, str]]:
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
    session: SQLSession,
) -> list[dict[str, int]]:
    update_request_count(session)
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
