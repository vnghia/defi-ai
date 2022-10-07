import os
from typing import TYPE_CHECKING, Any, Type, TypeVar

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

if TYPE_CHECKING:
    from sqlalchemy.sql.type_api import TypeEngine

    T = TypeVar("T")

    class Enum(TypeEngine[T]):
        def __init__(self, enum: Type[T], **kwargs: Any) -> None:
            ...

else:
    from sqlalchemy import Enum

SQL_USER = os.environ["SQL_USER"]
SQL_PASSWORD = os.environ["SQL_PASSWORD"]
SQL_HOST = os.environ["SQL_HOST"]
SQL_PORT = os.environ["SQL_PORT"]
SQL_SCRAPE_DATABASE = os.environ["SQL_SCRAPE_DATABASE"]


def create_engine_and_table(base) -> sqlalchemy.engine.Engine:
    connection_uri = sqlalchemy.engine.URL.create(
        "mysql",
        username=SQL_USER,
        password=SQL_PASSWORD,
        host=SQL_HOST,
        port=SQL_PORT,
        database=SQL_SCRAPE_DATABASE,
    )
    engine = sqlalchemy.create_engine(connection_uri, future=True, echo=False)
    base.metadata.create_all(engine)
    return engine


Base = declarative_base()
Engine = create_engine_and_table(Base)
Session = sessionmaker(Engine)
