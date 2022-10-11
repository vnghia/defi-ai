# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from defi_ai import scrape
from defi_ai.sql.base import SQLBase
from defi_ai.type import SQLSession
from sqlalchemy import Column, Integer, String, func, select
from sqlalchemy.orm import relationship


class Avatar(SQLBase):
    __tablename__ = "avatar"
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(32))
    requests = relationship(
        "Request", back_populates="avatar", cascade="all, delete", passive_deletes=True
    )

    def __repr__(self):
        return f"<Avatar(id={self.id}, name={self.name})>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.c}

    @classmethod
    def new(cls, session: SQLSession, name: str = None):
        if name is None:
            name = str(
                int(
                    session.get(
                        Avatar, session.execute(select(func.max(Avatar.id))).scalar()
                    ).name
                )
                + 1
            )
        id, name = scrape.create_user(name)
        avatar = cls(id=id, name=name)
        session.add(avatar)
        session.commit()
        return avatar.id

    @staticmethod
    def list_online():
        return scrape.list_users()

    @classmethod
    def update(cls, session: SQLSession):
        for user in cls.list_online():
            if not session.get(cls, user[0]):
                session.add(cls(id=user[0], name=user[1]))
        session.commit()

    @classmethod
    def from_name(cls, session: SQLSession, name: str):
        return session.execute(select(cls.id).filter(cls.name == name)).scalar()
