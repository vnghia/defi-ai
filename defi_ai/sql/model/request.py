# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Union

import pandas as pd
from defi_ai import scrape
from defi_ai.sql.base import SQLBase
from defi_ai.sql.model.avatar import Avatar
from defi_ai.sql.model.hotel import Hotel
from defi_ai.sql.model.response import Response
from defi_ai.sql.utils import execute_to_df
from defi_ai.type import City, Language, SQLSession
from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, func, select
from sqlalchemy.orm import relationship
from sqlalchemy.orm.util import AliasedClass


class Request(SQLBase):
    __tablename__ = "request"
    id = Column("id", Integer, primary_key=True)
    avatar_id = Column(
        "avatar_id", Integer, ForeignKey("avatar.id", ondelete="CASCADE")
    )
    language = Column("language", Enum(Language))
    city = Column("city", Enum(City))
    date = Column("date", Integer)
    mobile = Column("mobile", Boolean)
    responses = relationship(
        "Response",
        back_populates="request",
        cascade="all, delete",
        passive_deletes=True,
    )
    avatar = relationship("Avatar", back_populates="requests")

    def __repr__(self) -> str:
        return f"<Request(id={self.id}, avatar_id={self.avatar_id}, language={self.language}, city={self.city}, date={self.date}, mobile={self.mobile})>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.c}

    @classmethod
    def send(
        cls,
        session: SQLSession,
        avatar_id: int,
        language: Language,
        city: City,
        date: int,
        mobile: bool,
    ) -> Column[Integer]:
        avatar_name = session.get(Avatar, avatar_id).name
        prices = scrape.get_pricing(session, avatar_name, language, city, date, mobile)
        req = cls(
            avatar_id=avatar_id,
            language=language,
            city=city,
            date=date,
            mobile=mobile,
        )
        session.add(req)
        session.commit()
        session.refresh(req)
        Response.from_list(session, req.id, prices)
        session.commit()
        return req.id

    @staticmethod
    def get_count_statement(request: Union[Request, AliasedClass]):
        return select(
            request.id,
            func.rank()
            .over(partition_by=request.avatar_id, order_by=request.id)
            .label("request_count"),
            func.rank()
            .over(
                partition_by=[request.avatar_id, request.language],
                order_by=request.id,
            )
            .label("request_language_count"),
            func.rank()
            .over(partition_by=[request.avatar_id, request.city], order_by=request.id)
            .label("request_city_count"),
            func.rank()
            .over(partition_by=[request.avatar_id, request.date], order_by=request.id)
            .label("request_date_count"),
            func.rank()
            .over(
                partition_by=[request.avatar_id, request.mobile],
                order_by=request.id,
            )
            .label("request_mobile_count"),
        )

    @staticmethod
    def get_dataset_statement(
        request: Union[Request, AliasedClass], response: Union[Response, AliasedClass]
    ):
        hotel_count_subq = Hotel.get_count_statement().subquery()
        request_count_subq = Request.get_count_statement(request).subquery()
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
                request_count_subq.c.request_count,
                request_count_subq.c.request_language_count,
                request_count_subq.c.request_city_count,
                request_count_subq.c.request_date_count,
                request_count_subq.c.request_mobile_count,
                hotel_count_subq.c.hotel_city_count,
                hotel_count_subq.c.hotel_brand_count,
                hotel_count_subq.c.hotel_group_count,
                hotel_count_subq.c.hotel_city_group_count,
                hotel_count_subq.c.hotel_city_brand_count,
            )
            .join(Hotel, response.hotel_id == Hotel.id)
            .join(hotel_count_subq, response.hotel_id == hotel_count_subq.c.id)
            .join(request, response.request_id == request.id)
            .join(request_count_subq, request.id == request_count_subq.c.id)
        )

    @classmethod
    def load_dataset(
        cls, session: SQLSession, split_xy: bool = True, convert_category: bool = True
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        statement = (
            cls.get_dataset_statement(Request, Response)
            .add_columns(Response.price)
            .order_by(Response.id)
        )
        df = execute_to_df(session, statement, convert_category)
        if split_xy:
            return df.drop("price", axis=1), df[["price"]]
        else:
            return df
