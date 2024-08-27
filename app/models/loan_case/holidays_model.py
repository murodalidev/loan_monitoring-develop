from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, Date
from sqlalchemy.orm import relationship



class Holidays(Base):
    __tablename__='holidays'
    id=Column(Integer, primary_key=True)
    month_day = Column(String(10), nullable=True)
    class Config:
        orm_mode=True