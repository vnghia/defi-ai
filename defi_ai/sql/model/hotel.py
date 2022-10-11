# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import pandas as pd
from defi_ai.sql.base import SQLBase
from defi_ai.type import City, HotelBrand, HotelGroup, SQLSession
from sqlalchemy import Boolean, CheckConstraint, Column, Enum, Integer


class Hotel(SQLBase):
    __tablename__ = "hotel"
    __table_args__ = (CheckConstraint("0 <= children_policy AND children_policy <= 2"),)
    id = Column("id", Integer, primary_key=True, autoincrement=False)
    group = Column("group", Enum(HotelGroup))
    brand = Column("brand", Enum(HotelBrand))
    city = Column("city", Enum(City))
    parking = Column("parking", Boolean)
    pool = Column("pool", Boolean)
    children_policy = Column("children_policy", Integer)

    def __repr__(self):
        return f"<Hotel(id={self.id}, group={self.group.name}, brand={self.brand.name}, city={self.city}, parking={self.parking}, pool={self.pool}, children_policy={self.children_policy})>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.c}

    @classmethod
    def update(cls, session: SQLSession):
        df = pd.read_csv("dataset/features_hotels.csv").rename(
            columns={"hotel_id": "id"}
        )
        df.to_sql(cls.__tablename__, session.bind, if_exists="append", index=False)
