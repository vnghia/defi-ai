# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

import pandas as pd
from defi_ai.sql.base import SQLBase
from defi_ai.sql.model.avatar import Avatar
from defi_ai.sql.model.request import Request
from defi_ai.sql.utils import execute_to_df, is_kaggle
from defi_ai.type import City, Language, SQLSession
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Integer,
    select,
    update,
)
from sqlalchemy.orm import aliased, relationship, synonym


class Sample(SQLBase):
    __tablename__ = "sample"
    __table_args__ = (CheckConstraint("0 <= children_policy AND children_policy <= 2"),)

    id = Column("id", Integer, primary_key=True, autoincrement=False)
    order_requests = Column("order_requests", Integer)
    request_id = synonym("order_requests")
    avatar_id = Column("avatar_id", Integer)

    language = Column("language", Enum(Language))
    city = Column("city", Enum(City))
    date = Column("date", Integer)
    mobile = Column("mobile", Boolean)
    stock = Column("stock", Integer)

    scrape_request_id = Column(
        "scrape_request_id", Integer, ForeignKey("request.id", ondelete="SET NULL")
    )
    hotel_id = Column("hotel_id", Integer, ForeignKey("hotel.id"))
    hotel = relationship("Hotel")

    def __repr__(self) -> str:
        return f"<Sample(id={self.id}, order_requests={self.order_requests}, city={self.city}, date={self.date}, language={self.language}, mobile={self.mobile}, avatar_id={self.avatar_id}, hotel_id={self.hotel_id}, stock={self.stock})>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.c}

    @classmethod
    def update(cls, session: SQLSession):
        df = pd.read_csv("dataset/test_set.csv").rename(columns={"index": "id"})
        df["mobile"] = df["mobile"].astype(bool)
        df.to_sql(cls.__tablename__, session.bind, if_exists="append", index=False)

    @classmethod
    def scrape(cls, session: SQLSession):
        next_order_requests = session.execute(
            select(cls.order_requests)
            .where(cls.scrape_request_id.is_(None))
            .order_by(cls.order_requests)
            .offset(1)
        ).scalar()
        params = session.execute(
            select(
                cls.order_requests,
                cls.avatar_id,
                cls.language,
                cls.city,
                cls.date,
                cls.mobile,
            )
            .distinct()
            .order_by(cls.order_requests)
            .where(cls.order_requests >= next_order_requests)
        ).all()
        for param in params:
            req_id = Request.send(
                session,
                Avatar.from_name(session, f"sample-avatar-{param[1]}"),
                param[2],
                param[3],
                param[4],
                param[5],
            )
            session.execute(
                update(cls)
                .where(cls.order_requests == param[0])
                .values(scrape_request_id=req_id)
            )
            session.commit()

    @classmethod
    def load_dataset(cls, session: SQLSession) -> pd.DataFrame:
        if not is_kaggle:
            request_table = aliased(
                Request,
                select(
                    Sample.order_requests.label("id"),
                    Sample.avatar_id,
                    Sample.language,
                    Sample.city,
                    Sample.date,
                    Sample.mobile,
                )
                .distinct()
                .subquery(),
                adapt_on_names=True,
            )
            statement = Request.get_dataset_statement(request_table, Sample).order_by(
                Sample.id
            )
        else:
            statement = """SELECT anon_1.language, anon_1.city, anon_1.date, anon_1.mobile, hotel."group", hotel.brand, hotel.parking, hotel.pool, hotel.children_policy, sample.stock, anon_2.request_count, anon_2.request_language_count, anon_2.request_city_count, anon_2.request_date_count, anon_2.request_mobile_count, anon_3.hotel_city_count, anon_3.hotel_brand_count, anon_3.hotel_group_count, anon_3.hotel_city_group_count, anon_3.hotel_city_brand_count 
FROM sample JOIN hotel ON sample.hotel_id = hotel.id JOIN (SELECT hotel.id AS id, anon_4.count_1 AS hotel_city_count, anon_5.count_2 AS hotel_brand_count, anon_6.count_3 AS hotel_group_count, anon_7.count_4 AS hotel_city_group_count, anon_8.count_5 AS hotel_city_brand_count 
FROM hotel JOIN (SELECT hotel.city AS city, count(*) AS count_1 
FROM hotel GROUP BY hotel.city) AS anon_4 ON hotel.city = anon_4.city JOIN (SELECT hotel.brand AS brand, count(*) AS count_2 
FROM hotel GROUP BY hotel.brand) AS anon_5 ON hotel.brand = anon_5.brand JOIN (SELECT hotel."group" AS "group", count(*) AS count_3 
FROM hotel GROUP BY hotel."group") AS anon_6 ON hotel."group" = anon_6."group" JOIN (SELECT hotel.city AS city, hotel."group" AS "group", count(*) AS count_4 
FROM hotel GROUP BY hotel.city, hotel."group") AS anon_7 ON hotel.city = anon_7.city AND hotel."group" = anon_7."group" JOIN (SELECT hotel.city AS city, hotel.brand AS brand, count(*) AS count_5 
FROM hotel GROUP BY hotel.city, hotel.brand) AS anon_8 ON hotel.city = anon_8.city AND hotel.brand = anon_8.brand) AS anon_3 ON sample.hotel_id = anon_3.id JOIN (SELECT DISTINCT sample.order_requests AS id, sample.avatar_id AS avatar_id, sample.language AS language, sample.city AS city, sample.date AS date, sample.mobile AS mobile 
FROM sample) AS anon_1 ON sample.order_requests = anon_1.id JOIN (SELECT anon_1.id AS id, rank() OVER (PARTITION BY anon_1.avatar_id ORDER BY anon_1.id) AS request_count, rank() OVER (PARTITION BY anon_1.avatar_id, anon_1.language ORDER BY anon_1.id) AS request_language_count, rank() OVER (PARTITION BY anon_1.avatar_id, anon_1.city ORDER BY anon_1.id) AS request_city_count, rank() OVER (PARTITION BY anon_1.avatar_id, anon_1.date ORDER BY anon_1.id) AS request_date_count, rank() OVER (PARTITION BY anon_1.avatar_id, anon_1.mobile ORDER BY anon_1.id) AS request_mobile_count 
FROM (SELECT DISTINCT sample.order_requests AS id, sample.avatar_id AS avatar_id, sample.language AS language, sample.city AS city, sample.date AS date, sample.mobile AS mobile 
FROM sample) AS anon_1) AS anon_2 ON anon_1.id = anon_2.id ORDER BY sample.id"""
        return execute_to_df(
            session,
            statement,
            [
                "language",
                "city",
                "date",
                "mobile",
                "group",
                "brand",
                "parking",
                "pool",
                "children_policy",
                "stock",
                "request_count",
                "request_language_count",
                "request_city_count",
                "request_date_count",
                "request_mobile_count",
                "hotel_city_count",
                "hotel_brand_count",
                "hotel_group_count",
                "hotel_city_group_count",
                "hotel_city_brand_count",
            ],
        )
