import os
from datetime import date
from posixpath import join as urljoin

import requests
from sqlalchemy import Column, Date, Integer

from req_enums import City, Language
from sql_global import Base, Session

HOST_URL = os.environ["HOST_URL"]
USER_ID = os.environ["USER_ID"]

today = date.today()


class RequestCount(Base):
    __tablename__ = "request_count"
    date = Column("date", Date, primary_key=True)
    count = Column("count", Integer)

    def __repr__(self):
        return f"<RequestCount(date={self.date}, count={self.count})>"

    @classmethod
    def list(cls):
        with Session() as session:
            return session.query(cls).all()


def update_request_count():
    with Session() as session:
        rc = session.get(RequestCount, today)
        if rc is None:
            session.add(RequestCount(date=today, count=1))
        else:
            rc.count += 1
        session.commit()


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
