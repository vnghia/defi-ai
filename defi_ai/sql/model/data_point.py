# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import pandas as pd
from defi_ai.sql.base import SQLBase
from defi_ai.sql.model.hotel import Hotel
from defi_ai.sql.model.request import Request
from defi_ai.sql.model.response import Response
from defi_ai.type import City, HotelBrand, HotelGroup, Language, SQLSession
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Integer,
    func,
    select,
)


class DataPoint(SQLBase):
    __tablename__ = "data_point"
    __table_args__ = (CheckConstraint("0 <= children_policy AND children_policy <= 2"),)

    id = Column("id", Integer, primary_key=True)
    avatar_id = Column(
        "avatar_id", Integer, ForeignKey("avatar.id", ondelete="CASCADE")
    )

    language = Column("language", Enum(Language))
    city = Column("city", Enum(City))
    date = Column("date", Integer)
    mobile = Column("mobile", Boolean)
    group = Column("group", Enum(HotelGroup))
    brand = Column("brand", Enum(HotelBrand))
    parking = Column("parking", Boolean)
    pool = Column("pool", Boolean)
    children_policy = Column("children_policy", Integer)
    stock = Column("stock", Integer)

    request_count = Column("request_count", Integer)
    request_language_count = Column("request_language_count", Integer)
    request_city_count = Column("request_city_count", Integer)
    request_date_count = Column("request_date_count", Integer)
    request_mobile_count = Column("request_mobile_count", Integer)

    price = Column("price", Integer)

    response_id = Column(
        "response_id", Integer, ForeignKey("response.id", ondelete="CASCADE")
    )

    def __repr__(self) -> str:
        return f"<DataPoint(id={self.id}, avatar_id={self.avatar_id}, language={self.language}, city={self.city}, date={self.date}, mobile={self.mobile}, group={self.group.name}, brand={self.brand.name}, parking={self.parking}, pool={self.pool}, children_policy={self.children_policy}, stock={self.stock}, request_count={self.request_count}, request_language_count={self.request_language_count}, request_city_count={self.request_city_count}, request_date_count={self.request_date_count}, request_mobile_count={self.request_mobile_count}, price={self.price}, response_id={self.response_id})>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.c}

    @classmethod
    def update(cls, session: SQLSession):
        current_response_id = (
            session.execute(select(func.max(cls.response_id))).scalar() or 0
        )
        subq_count = select(
            Request.id,
            func.rank()
            .over(partition_by=Request.avatar_id, order_by=Request.id)
            .label("request_count"),
            func.rank()
            .over(
                partition_by=[Request.avatar_id, Request.language],
                order_by=Request.id,
            )
            .label("request_language_count"),
            func.rank()
            .over(partition_by=[Request.avatar_id, Request.city], order_by=Request.id)
            .label("request_city_count"),
            func.rank()
            .over(partition_by=[Request.avatar_id, Request.date], order_by=Request.id)
            .label("request_date_count"),
            func.rank()
            .over(
                partition_by=[Request.avatar_id, Request.mobile],
                order_by=Request.id,
            )
            .label("request_mobile_count"),
        ).subquery()
        next_responses = session.execute(
            select(
                Request.avatar_id,
                Request.language,
                Request.city,
                Request.date,
                Request.mobile,
                Hotel.group,
                Hotel.brand,
                Hotel.parking,
                Hotel.pool,
                Hotel.children_policy,
                Response.stock,
                subq_count.c.request_count,
                subq_count.c.request_language_count,
                subq_count.c.request_city_count,
                subq_count.c.request_date_count,
                subq_count.c.request_mobile_count,
                Response.price,
                Response.id.label("response_id"),
            )
            .join(Response.hotel)
            .join(Response.request)
            .join(subq_count, Request.id == subq_count.c.id)
            .filter(Response.id > current_response_id)
        ).all()
        session.add_all([cls(**response._mapping) for response in next_responses])
        session.commit()

    @classmethod
    def load_dataset(cls, session: SQLSession) -> tuple[pd.DataFrame, pd.DataFrame]:
        rows = session.execute(
            select(
                cls.language,
                cls.city,
                cls.date,
                cls.mobile,
                cls.parking,
                cls.pool,
                cls.children_policy,
                cls.stock,
                cls.request_count,
                cls.request_language_count,
                cls.request_city_count,
                cls.request_date_count,
                cls.request_mobile_count,
                cls.price,
            ).distinct()
        ).all()
        df = pd.DataFrame([row._mapping for row in rows])
        df = df[
            [
                "language",
                "city",
                "date",
                "mobile",
                "parking",
                "pool",
                "children_policy",
                "stock",
                "request_count",
                "request_language_count",
                "request_city_count",
                "request_date_count",
                "request_mobile_count",
                "price",
            ]
        ]
        df_x = df.drop("price", axis=1)
        df_y = df[["price"]]
        return df_x, df_y
