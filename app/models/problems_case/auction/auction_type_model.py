from app.db.connect_db import Base
from sqlalchemy import String, Integer, Column, Integer, Text
from sqlalchemy.orm import relationship

class ProblemsAuctionType(Base):
    __tablename__='problems_auction_type'
    id=Column(Integer, primary_key=True)
    name = Column(Text, nullable = True)
    code = Column(String(30), nullable = True)
    auction = relationship('ProblemsAuction', backref='type')
    class Config:
        orm_mode=True