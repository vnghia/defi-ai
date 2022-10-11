import pandas as pd
from defi_ai.sql.base import SQLBase
from defi_ai.type import City, Language, SQLSession
from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer


class Sample(SQLBase):
    __tablename__ = "sample"
    id = Column("id", Integer, primary_key=True, autoincrement=False)
    order_requests = Column("order_requests", Integer)
    city = Column("city", Enum(City))
    date = Column("date", Integer)
    language = Column("language", Enum(Language))
    mobile = Column("mobile", Boolean)
    avatar_id = Column("avatar_id", Integer)
    hotel_id = Column("hotel_id", Integer, ForeignKey("hotel.id"))
    stock = Column("stock", Integer)

    def __repr__(self):
        return f"<Sample(id={self.id}, order_requests={self.order_requests}, city={self.city}, date={self.date}, language={self.language}, mobile={self.mobile}, avatar_id={self.avatar_id}, hotel_id={self.hotel_id}, stock={self.stock})>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.c}

    @classmethod
    def update(cls, session: SQLSession):
        df = pd.read_csv("dataset/test_set.csv").rename(columns={"index": "id"})
        df.to_sql(cls.__tablename__, session.bind, if_exists="append", index=False)
