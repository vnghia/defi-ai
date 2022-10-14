# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import pandas as pd
from defi_ai.sql.base import SQLBase
from defi_ai.type import City, HotelBrand, HotelGroup, SQLSession
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Enum,
    Integer,
    func,
    select,
    and_,
)
from sqlalchemy.orm import relationship


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
    responses = relationship(
        "Response", back_populates="hotel", cascade="all, delete", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Hotel(id={self.id}, group={self.group.name}, brand={self.brand.name}, city={self.city}, parking={self.parking}, pool={self.pool}, children_policy={self.children_policy})>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.c}

    @classmethod
    def update(cls, session: SQLSession):
        df = pd.read_csv("dataset/features_hotels.csv").rename(
            columns={"hotel_id": "id"}
        )
        df["parking"] = df["parking"].astype(bool)
        df["pool"] = df["pool"].astype(bool)
        df.to_sql(cls.__tablename__, session.bind, if_exists="append", index=False)

    @classmethod
    def get_count_statement(cls):
        hotel_city_count = select(cls.city, func.count()).group_by(cls.city).subquery()
        hotel_brand_count = (
            select(cls.brand, func.count()).group_by(cls.brand).subquery()
        )
        hotel_group_count = (
            select(cls.group, func.count()).group_by(cls.group).subquery()
        )
        hotel_city_group_count = (
            select(cls.city, cls.group, func.count())
            .group_by(cls.city, cls.group)
            .subquery()
        )
        hotel_city_brand_count = (
            select(cls.city, cls.brand, func.count())
            .group_by(cls.city, cls.brand)
            .subquery()
        )
        return (
            select(
                cls.id,
                hotel_city_count.c.count.label("hotel_city_count"),
                hotel_brand_count.c.count.label("hotel_brand_count"),
                hotel_group_count.c.count.label("hotel_group_count"),
                hotel_city_group_count.c.count.label("hotel_city_group_count"),
                hotel_city_brand_count.c.count.label("hotel_city_brand_count"),
            )
            .join(hotel_city_count, cls.city == hotel_city_count.c.city)
            .join(hotel_brand_count, cls.brand == hotel_brand_count.c.brand)
            .join(hotel_group_count, cls.group == hotel_group_count.c.group)
            .join(
                hotel_city_group_count,
                and_(
                    cls.city == hotel_city_group_count.c.city,
                    cls.group == hotel_city_group_count.c.group,
                ),
            )
            .join(
                hotel_city_brand_count,
                and_(
                    cls.city == hotel_city_brand_count.c.city,
                    cls.brand == hotel_city_brand_count.c.brand,
                ),
            )
        )
