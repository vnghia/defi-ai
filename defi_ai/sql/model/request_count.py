# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from defi_ai.sql.base import SQLBase
from sqlalchemy import Column, Date, Integer
from defi_ai.type import SQLSession


class RequestCount(SQLBase):
    __tablename__ = "request_count"
    date = Column("date", Date, primary_key=True)
    count = Column("count", Integer)

    def __repr__(self: RequestCount) -> str:
        return f"<RequestCount(date={self.date}, count={self.count})>"

    @classmethod
    def list(cls: type[RequestCount], session: SQLSession):
        return session.query(cls).all()