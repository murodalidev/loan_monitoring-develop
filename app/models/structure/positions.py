from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class Positions(Base):
    __tablename__='positions'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    employee = relationship('Users', backref='pos')
    class Config:
        orm_mode=True