# SPDX-FileCopyrightText: 2022-present Vo Van Nghia <vanvnghia@gmail.com>
#
# SPDX-License-Identifier: MIT

import pandas as pd
from defi_ai.sql.base import SQLBase
from defi_ai.sql.model.avatar import Avatar
from defi_ai.sql.model.request import Request
from defi_ai.sql.utils import execute_to_df
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
    def load_dataset(
        cls, session: SQLSession, convert_category: bool = True
    ) -> pd.DataFrame:
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
        return execute_to_df(session, statement, convert_category)
