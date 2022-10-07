from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

import scrape
from avatar import Avatar
from req_enums import City, Language
from res import Response
from sql_global import Base, Enum, Session


class Request(Base):
    __tablename__ = "request"
    id = Column("id", Integer, primary_key=True)
    avatar_id = Column("avatar_id", Integer, ForeignKey("avatar.id"))
    language = Column("language", Enum(Language))
    city = Column("city", Enum(City))
    date = Column("date", Integer)
    mobile = Column("mobile", Boolean)
    responses = relationship("Response", back_populates="request")
    avatar = relationship("Avatar", back_populates="requests")

    def __repr__(self):
        return f"<Request(id={self.id}, avatar_id={self.avatar_id}, language={self.language}, city={self.city}, date={self.date}, mobile={self.mobile})>"

    @classmethod
    def send(
        cls,
        avatar_id: int,
        language: Language,
        city: City,
        date: int,
        mobile: bool,
    ):
        with Session() as session:
            avatar_name = session.get(Avatar, avatar_id).name
            prices = scrape.get_pricing(avatar_name, language, city, date, mobile)
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
            res = Response.from_list(req.id, prices, session)
            session.commit()
            for r in res:
                session.refresh(r)
            return res

    @classmethod
    def list(cls):
        with Session() as session:
            return session.query(cls).all()
