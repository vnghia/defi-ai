from sqlalchemy import Column, Integer, String

import sql_global

import scrape


class Avatar(sql_global.Base):
    __tablename__ = "avatar"
    id = Column("avatar_id", Integer, primary_key=True)
    name = Column("avatar_name", String(32))

    @classmethod
    def new(cls, name: str):
        id, name = scrape.create_user(name)
        avatar = cls(id=id, name=name)
        with sql_global.Session() as session:
            session.add(avatar)
            session.commit()
        return avatar
