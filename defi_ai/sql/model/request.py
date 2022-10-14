# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Union

from defi_ai import scrape
from defi_ai.sql.base import SQLBase
from defi_ai.sql.model.avatar import Avatar
from defi_ai.sql.model.response import Response
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
