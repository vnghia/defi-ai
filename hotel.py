import enum

import pandas as pd
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from req_enums import City
from sql_global import Base, Engine, Enum

ChildrenPolicy = enum.Enum("ChildrenPolicy", "0 1 2")


class Hotel(Base):
    __tablename__ = "hotel"
    id = Column("id", Integer, primary_key=True, autoincrement=False)
    group = Column("group", String(64))
    brand = Column("brand", String(64))
    city = Column("city", Enum(City))
    parking = Column("parking", Boolean)
    pool = Column("pool", Boolean)
    children_policy = Column("children_policy", Enum(ChildrenPolicy))
    responses = relationship("Response")

    @classmethod
    def update(cls):
        df = pd.read_csv("dataset/features_hotels.csv").rename(
            columns={"hotel_id": "id"}
        )
        df["children_policy"] = df["children_policy"].astype(str)
        df.to_sql(
            cls.__tablename__,
            Engine,
            if_exists="append",
            index=False,
            dtype={c.name: c.type for c in cls.__table__.c},
        )
