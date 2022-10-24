# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import uuid
from typing import Optional

from defi_ai import scrape
from defi_ai.sql.base import SQLBase
from defi_ai.type import SQLSession
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.orm import relationship


class Avatar(SQLBase):
    __tablename__ = "avatar"
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(64), unique=True, index=True)
    server_id = Column("server_id", Integer)
    server_name = Column("server_name", String(64))
    requests = relationship(
        "Request", back_populates="avatar", cascade="all, delete", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Avatar(id={self.id}, name={self.name})>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.c}

    @classmethod
    def new(
        cls, session: SQLSession, name: str = None, server_name: str = None
    ) -> Column[String]:
        server_name = server_name or uuid.uuid4().hex
        name = name or f"random_{uuid.uuid4().hex[:6]}"
        server_id, server_name = scrape.create_user(server_name)
        avatar = cls(name=name, server_id=server_id, server_name=server_name)
        session.add(avatar)
        session.commit()
        return avatar.name

    @staticmethod
    def list_online() -> list[tuple[int, str]]:
        return scrape.list_users()

    @classmethod
    def from_name(cls, session: SQLSession, name: str) -> Optional[tuple[int, str]]:
        return session.execute(
            select(cls.id, cls.server_name).filter(cls.name == name)
        ).one()
