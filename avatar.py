from sqlalchemy import Column, Integer, String

import scrape
import sql_global


class Avatar(sql_global.Base):
    __tablename__ = "avatar"
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(32))

    def __repr__(self):
        return f"<Avatar(id={self.id}, name={self.name})>"

    @classmethod
    def new(cls, name: str):
        id, name = scrape.create_user(name)
        avatar = cls(id=id, name=name)
        with sql_global.Session() as session:
            session.add(avatar)
            session.commit()
        return avatar

    @classmethod
    def list(cls):
        with sql_global.Session() as session:
            return session.query(cls).all()

    @staticmethod
    def list_online():
        return scrape.list_users()

    @classmethod
    def update(cls):
        with sql_global.Session() as session:
            for user in cls.list_online():
                if not session.get(cls, user[0]):
                    session.add(cls(id=user[0], name=user[1]))
            session.commit()
