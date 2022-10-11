# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from defi_ai.sql.base import SQLBase
from defi_ai.type import SQLSession
from sqlalchemy import Column, ForeignKey, Integer


class Response(SQLBase):
    __tablename__ = "response"
    id = Column("id", Integer, primary_key=True)
    request_id = Column(
        "request_id", Integer, ForeignKey("request.id", ondelete="CASCADE")
    )
    hotel_id = Column("hotel_id", Integer, ForeignKey("hotel.id", ondelete="CASCADE"))
    price = Column("price", Integer)
    stock = Column("stock", Integer)

    def __repr__(self) -> str:
        return f"<Response(id={self.id}, request_id={self.request_id}, hotel_id={self.hotel_id}, price={self.price}, stock={self.stock})>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.c}

    @classmethod
    def from_list(
        cls, session: SQLSession, request_id: int, prices: list[dict[str, int]]
    ):
        results = []
        for price in prices:
            results.append(
                cls(
                    request_id=request_id,
                    hotel_id=price["hotel_id"],
                    price=price["price"],
                    stock=price["stock"],
                )
            )
        session.add_all(results)
