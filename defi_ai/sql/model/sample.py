import pandas as pd
from defi_ai.sql.base import SQLBase
from defi_ai.sql.model.hotel import Hotel
from defi_ai.type import City, HotelBrand, HotelGroup, Language, SQLSession
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Integer,
    select,
)
from sqlalchemy.orm import relationship


class Sample(SQLBase):
    __tablename__ = "sample"
    __table_args__ = (CheckConstraint("0 <= children_policy AND children_policy <= 2"),)

    id = Column("id", Integer, primary_key=True, autoincrement=False)
    order_requests = Column("order_requests", Integer)
    avatar_id = Column("avatar_id", Integer)

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

    scrape_request_id = Column(
        "request_id", Integer, ForeignKey("request.id", ondelete="SET NULL")
    )
    hotel_id = Column("hotel_id", Integer, ForeignKey("hotel.id"))
    hotel = relationship("Hotel")

    def __repr__(self) -> str:
        return f"<Sample(id={self.id}, order_requests={self.order_requests}, avatar_id={self.avatar_id}, language={self.language}, city={self.city}, date={self.date}, mobile={self.mobile}, group={self.group.name}, brand={self.brand.name}, parking={self.parking}, pool={self.pool}, children_policy={self.children_policy}, stock={self.stock}, request_count={self.request_count}, request_language_count={self.request_language_count}, request_city_count={self.request_city_count}, request_date_count={self.request_date_count}, request_mobile_count={self.request_mobile_count}, hotel_id={self.hotel_id})>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.c}

    @classmethod
    def update(cls, session: SQLSession):
        df = pd.read_csv("dataset/test_set.csv").rename(columns={"index": "id"})
        df["mobile"] = df["mobile"].astype(bool)
        df_hotel = pd.DataFrame(
            [
                row._mapping
                for row in session.execute(
                    select(
                        Hotel.group,
                        Hotel.brand,
                        Hotel.parking,
                        Hotel.pool,
                        Hotel.children_policy,
                    ).order_by(Hotel.id)
                ).all()
            ]
        )
        df = df.join(df_hotel, on="hotel_id")
        df["brand"] = df["brand"].apply(lambda x: HotelBrand(x).name)
        df["group"] = df["group"].apply(lambda x: HotelGroup(x).name)
        df_count = df[
            ["avatar_id", "order_requests", "language", "city", "date", "mobile"]
        ].drop_duplicates("order_requests")
        df_count["request_count"] = (
            df_count.groupby(["avatar_id"])["order_requests"].rank("min").astype(int)
        )
        for i in ["language", "city", "date", "mobile"]:
            df_count[f"request_{i}_count"] = (
                df_count.groupby(["avatar_id", i])["order_requests"]
                .rank("min")
                .astype(int)
            )
        df = df.join(
            df_count[
                [
                    "order_requests",
                    "request_count",
                    "request_language_count",
                    "request_city_count",
                    "request_date_count",
                    "request_mobile_count",
                ]
            ].set_index("order_requests"),
            on="order_requests",
        )
        df.to_sql(cls.__tablename__, session.bind, if_exists="append", index=False)
