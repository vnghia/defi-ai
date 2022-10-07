from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

import scrape
import sql_global
from avatar import Avatar
from req_enums import City, Language
from res import Response


class Request(sql_global.Base):
    __tablename__ = "request"
    id = Column("id", Integer, primary_key=True)
    avatar_id = Column("avatar_id", Integer, ForeignKey("avatar.id"))
    language = Column("language", sql_global.Enum(Language))
    city = Column("city", sql_global.Enum(City))
    date = Column("date", Integer)
    mobile = Column("mobile", Boolean)
    responses = relationship("Response")

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
        avatar_name = sql_global.Session().get(Avatar, avatar_id).name
        prices = scrape.get_pricing(avatar_name, language, city, date, mobile)
        req = cls(
            avatar_id=avatar_id, language=language, city=city, date=date, mobile=mobile
        )
        req_id = None
        with sql_global.Session() as session:
            session.add(req)
            session.commit()
            req_id = req.id
        res = Response.from_list(req_id, prices)
        return req, res
