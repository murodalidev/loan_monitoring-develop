from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer





class checked_status(Base):
    __tablename__='checked_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(20))
    class Config:
        orm_mode=True