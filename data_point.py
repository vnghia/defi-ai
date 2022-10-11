import pandas as pd
from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, func

from hotel import Hotel
from req import Request
from req_enums import City, HotelBrand, HotelGroup, Language
from res import Response
from sql_global import Base, Enum, Session


class DataPoint(Base):
    __tablename__ = "data_point"
    __table_args__ = (CheckConstraint("0 <= children_policy AND children_policy <= 2"),)
    id = Column("id", Integer, primary_key=True)
    avatar_id = Column(
        "avatar_id", Integer, ForeignKey("avatar.id", ondelete="CASCADE")
    )
    language = Column("language", Enum(Language))
    city = Column("city", Enum(City))
    date = Column("date", Integer)
    mobile = Column("mobile", Boolean)
    group = Column("group", Enum(HotelGroup))
    brand = Column("brand", Enum(HotelBrand))
    parking = Column("parking", Boolean)
    pool = Column("pool", Boolean)
    children_policy = Column("children_policy", Integer)
    stock = Column("stock", Integer)

    request_count = Column("request_count", Integer)
    request_language_count = Column("request_language_count", Integer)
    request_city_count = Column("request_city_count", Integer)
    request_date_count = Column("request_date_count", Integer)
    request_mobile_count = Column("request_mobile_count", Integer)

    price = Column("price", Integer)

    response_id = Column(
        "response_id", Integer, ForeignKey("response.id", ondelete="CASCADE")
    )
    sample_id = Column(
        "sample_id", Integer, ForeignKey("sample.id", ondelete="CASCADE")
    )

    def __repr__(self):
        return f"<DataPoint(id={self.id}, avatar_id={self.avatar_id}, language={self.language}, city={self.city}, date={self.date}, mobile={self.mobile}, group={self.group.name}, brand={self.brand.name}, parking={self.parking}, pool={self.pool}, children_policy={self.children_policy}, stock={self.stock}, request_count={self.request_count}, request_language_count={self.request_language_count}, request_city_count={self.request_city_count}, request_date_count={self.request_date_count}, request_mobile_count={self.request_mobile_count}, price={self.price}, response_id={self.response_id}, sample_id={self.sample_id})>"

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.c}

    @classmethod
    def update_from_response(cls):
        with Session() as session:
            current_response_id = session.query(func.max(cls.response_id)).scalar() or 0
            subq_count = session.query(
                Request.id,
                func.rank()
                .over(partition_by=Request.avatar_id, order_by=Request.id)
                .label("request_count"),
                func.rank()
                .over(
                    partition_by=[Request.avatar_id, Request.language],
                    order_by=Request.id,
                )
                .label("request_language_count"),
                func.rank()
                .over(
                    partition_by=[Request.avatar_id, Request.city], order_by=Request.id
                )
                .label("request_city_count"),
                func.rank()
                .over(
                    partition_by=[Request.avatar_id, Request.date], order_by=Request.id
                )
                .label("request_date_count"),
                func.rank()
                .over(
                    partition_by=[Request.avatar_id, Request.mobile],
                    order_by=Request.id,
                )
                .label("request_mobile_count"),
            ).subquery()
            next_responses = (
                session.query(
                    Request.avatar_id,
                    Request.language,
                    Request.city,
                    Request.date,
                    Request.mobile,
                    Hotel.group,
                    Hotel.brand,
                    Hotel.parking,
                    Hotel.pool,
                    Hotel.children_policy,
                    Response.stock,
                    subq_count.c.request_count,
                    subq_count.c.request_language_count,
                    subq_count.c.request_city_count,
                    subq_count.c.request_date_count,
                    subq_count.c.request_mobile_count,
                    Response.price,
                    Response.id.label("response_id"),
                )
                .join(Response.hotel)
                .join(Response.request)
                .join(subq_count, Request.id == subq_count.c.id)
                .filter(Response.id >= current_response_id)
                .all()
            )
            session.add_all([cls(**response._mapping) for response in next_responses])
            session.commit()

    @classmethod
    def load_dataset(cls):
        with Session() as session:
            rows = (
                session.query(
                    cls.language,
                    cls.city,
                    cls.date,
                    cls.mobile,
                    cls.parking,
                    cls.pool,
                    cls.children_policy,
                    cls.stock,
                    cls.request_count,
                    cls.request_language_count,
                    cls.request_city_count,
                    cls.request_date_count,
                    cls.request_mobile_count,
                    cls.price,
                )
                .filter(cls.response_id.is_not(None))
                .all()
            )
            df = pd.DataFrame([row._mapping for row in rows])
            df = df[
                [
                    "language",
                    "city",
                    "date",
                    "mobile",
                    "parking",
                    "pool",
                    "children_policy",
                    "stock",
                    "request_count",
                    "request_language_count",
                    "request_city_count",
                    "request_date_count",
                    "request_mobile_count",
                    "price",
                ]
            ]
            df_x = df.drop("price", axis=1)
            df_y = df["price"]
            return df_x, df_y
