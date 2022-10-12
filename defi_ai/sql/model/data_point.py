# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Union

import pandas as pd
from defi_ai.sql.base import SQLBase
from defi_ai.sql.model.hotel import Hotel
from defi_ai.sql.model.request import Request
from defi_ai.sql.model.response import Response
from defi_ai.sql.model.sample import Sample
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
from sqlalchemy.orm import aliased
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql.expression import Subquery


class DataPoint(SQLBase):
    __tablename__ = "data_point"
    __table_args__ = (CheckConstraint("0 <= children_policy AND children_policy <= 2"),)
    id = Column("id", Integer, primary_key=True)
    avatar_id = Column(
        "avatar_id", Integer, ForeignKey("avatar.id", ondelete="CASCADE")
    )
    sample_avatar_id = Column("sample_avatar_id", Integer)
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
    sample_id = Column(
        "sample_id", Integer, ForeignKey("sample.id", ondelete="CASCADE")
    )

    request_like_sample_statement = select(
        Sample.order_requests.label("id"),
        Sample.avatar_id,
        Sample.language,
        Sample.city,
        Sample.date,
        Sample.mobile,
    ).distinct()

    def __repr__(self) -> str:
        return f"<DataPoint(id={self.id}, avatar_id={self.avatar_id}, language={self.language}, city={self.city}, date={self.date}, mobile={self.mobile}, group={self.group.name}, brand={self.brand.name}, parking={self.parking}, pool={self.pool}, children_policy={self.children_policy}, stock={self.stock}, request_count={self.request_count}, request_language_count={self.request_language_count}, request_city_count={self.request_city_count}, request_date_count={self.request_date_count}, request_mobile_count={self.request_mobile_count}, price={self.price}, response_id={self.response_id}, sample_id={self.sample_id})>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.c}

    @classmethod
    def __get_count_statement(cls, table: Union[SQLBase, AliasedClass]) -> select:
        return select(
            table.id,
            func.rank()
            .over(partition_by=table.avatar_id, order_by=table.id)
            .label("request_count"),
            func.rank()
            .over(
                partition_by=[table.avatar_id, table.language],
                order_by=table.id,
            )
            .label("request_language_count"),
            func.rank()
            .over(partition_by=[table.avatar_id, table.city], order_by=table.id)
            .label("request_city_count"),
            func.rank()
            .over(partition_by=[table.avatar_id, table.date], order_by=table.id)
            .label("request_date_count"),
            func.rank()
            .over(
                partition_by=[table.avatar_id, table.mobile],
                order_by=table.id,
            )
            .label("request_mobile_count"),
        )

    @classmethod
    def __get_data_point_select(
        cls,
        request: Union[SQLBase, AliasedClass],
        response: SQLBase,
        count: Subquery,
    ):
        return (
            select(
                request.language,
                request.city,
                request.date,
                request.mobile,
                Hotel.group,
                Hotel.brand,
                Hotel.parking,
                Hotel.pool,
                Hotel.children_policy,
                response.stock,
                count.c.request_count,
                count.c.request_language_count,
                count.c.request_city_count,
                count.c.request_date_count,
                count.c.request_mobile_count,
            )
            .join(response.hotel)
            .join(request, response.request_id == request.id)
            .join(count, request.id == count.c.id)
        )

    @classmethod
    def update_from_response(cls, session: SQLSession):
        current_response_id = (
            session.execute(select(func.max(cls.response_id))).scalar() or 0
        )
        subq_count = cls.__get_count_statement(Request).subquery()
        next_responses = session.execute(
            cls.__get_data_point_select(Request, Response, subq_count)
            .add_columns(
                Request.avatar_id, Response.price, Response.id.label("response_id")
            )
            .filter(Response.id > current_response_id)
        ).all()
        session.add_all([cls(**response._mapping) for response in next_responses])
        session.commit()

    @classmethod
    def update_from_sample(cls, session: SQLSession):
        current_sample_id = (
            session.execute(select(func.max(DataPoint.sample_id))).scalar() or -1
        )
        request_table = aliased(
            Request,
            cls.request_like_sample_statement.filter(
                Sample.id > current_sample_id
            ).subquery(),
            adapt_on_names=True,
        )
        subq_count = cls.__get_count_statement(request_table).subquery()
        next_responses = session.execute(
            cls.__get_data_point_select(request_table, Sample, subq_count)
            .add_columns(
                Sample.avatar_id.label("sample_avatar_id"), Sample.id.label("sample_id")
            )
            .filter(Sample.id > current_sample_id)
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
            ).filter(cls.response_id.is_not(None))
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
