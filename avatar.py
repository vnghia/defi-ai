from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

import scrape
from sql_global import Base, Session


class Avatar(Base):
    __tablename__ = "avatar"
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(32))
    requests = relationship("Request", back_populates="avatar")

    def __repr__(self):
        return f"<Avatar(id={self.id}, name={self.name})>"

    @classmethod
    def new(cls, name: str):
        id, name = scrape.create_user(name)
        avatar = cls(id=id, name=name)
        with Session() as session:
            session.add(avatar)
            session.commit()
        return avatar

    @classmethod
    def list(cls):
        with Session() as session:
            return session.query(cls).all()

    @staticmethod
    def list_online():
        return scrape.list_users()

    @classmethod
    def update(cls):
        with Session() as session:
            for user in cls.list_online():
                if not session.get(cls, user[0]):
                    session.add(cls(id=user[0], name=user[1]))
            session.commit()
