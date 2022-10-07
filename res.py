from sqlalchemy import Column, ForeignKey, Integer

import sql_global


class Response(sql_global.Base):
    __tablename__ = "response"
    id = Column("id", Integer, primary_key=True)
    request_id = Column("request_id", Integer, ForeignKey("request.id"))
    hotel_id = Column("hotel_id", Integer, ForeignKey("hotel.id"))
    price = Column("price", Integer)
    stock = Column("stock", Integer)

    def __repr__(self):
        return f"<Response(id={self.id}, request_id={self.request_id}, hotel_id={self.hotel_id}, price={self.price}, stock={self.stock})>"

    @classmethod
    def from_list(cls, request_id: int, prices: list[dict[str, int]]):
        results = []
        for price in prices:
            results.append(
                cls(
                    request_id=request_id,
                    hotel_id=price["hotel_id"],
                    price=price["price"],
                    stock=price["stock"],
                )
            )
        with sql_global.Session() as session:
            session.add_all(results)
            session.commit()
        return results
