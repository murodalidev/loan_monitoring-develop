from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class FromType(Base):
    __tablename__='from_type'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    code = Column(Integer, nullable=True)
    business = relationship('BusinessCase', backref='from_type')
    class Config:
        orm_mode=True