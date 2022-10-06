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


def create_engine_and_table(base) -> sqlalchemy.engine.Engine:
    engine = sqlalchemy.create_engine(
        "sqlite+pysqlite:///dataset.db", future=True, echo=False
    )
    base.metadata.create_all(engine)
    return engine


Base = declarative_base()
Engine = create_engine_and_table(Base)
Session = sessionmaker(Engine)
