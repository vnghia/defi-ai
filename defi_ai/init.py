# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import os

import sqlalchemy
from sqlalchemy.orm import DeclarativeMeta, sessionmaker

from defi_ai.sql.base import SQLBase
from defi_ai.sql.model.avatar import Avatar  # noqa: F401
from defi_ai.sql.model.data_point import DataPoint  # noqa: F401
from defi_ai.sql.model.hotel import Hotel  # noqa: F401
from defi_ai.sql.model.request import Request  # noqa: F401
from defi_ai.sql.model.request_count import RequestCount  # noqa: F401
from defi_ai.sql.model.response import Response  # noqa: F401
from defi_ai.type import SQLEngine


def create_engine_and_table(
    base: type[DeclarativeMeta],
    username: str,
    password: str,
    host: str,
    port: int,
    database: str,
) -> SQLEngine:
    connection_uri = sqlalchemy.engine.URL.create(
        "mysql",
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
    )
    engine = sqlalchemy.create_engine(connection_uri, future=True, echo=False)
    base.metadata.create_all(engine)
    return engine


def init_session(
    username: str = None,
    password: str = None,
    host: str = None,
    port: int = None,
    database: str = None,
) -> sessionmaker:
    username = username or os.environ["SQL_USERNAME"]
    password = password or os.environ["SQL_PASSWORD"]
    host = host or os.environ["SQL_HOST"]
    port = port or int(os.environ["SQL_PORT"])
    database = database or os.environ["SQL_SCRAPE_DATABASE"]
    engine = create_engine_and_table(SQLBase, username, password, host, port, database)
    Session: sessionmaker = sessionmaker(engine)
    return Session
