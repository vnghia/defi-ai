import enum

import pandas as pd
from sqlalchemy import Boolean, Column, Integer, String

import sql_global
from req_enums import City

ChildrenPolicy = enum.Enum("ChildrenPolicy", "0 1 2")


class Hotel(sql_global.Base):
    __tablename__ = "hotel"
    id = Column("id", Integer, primary_key=True)
    group = Column("group", String(64))
    brand = Column("brand", String(64))
    city = Column("city", sql_global.Enum(City))
    parking = Column("parking", Boolean)
    pool = Column("pool", Boolean)
    children_policy = Column("children_policy", sql_global.Enum(ChildrenPolicy))

    @classmethod
    def update(cls):
        df = pd.read_csv("dataset/features_hotels.csv")
        df.to_sql(cls.__tablename__, sql_global.Engine, if_exists="append", index=False)
