from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, Table, ForeignKey
from sqlalchemy.orm import relationship





class permission_category(Base):
    __tablename__='permission_category'
    id=Column(Integer, primary_key=True)
    name = Column(String(100))
    endpoint = relationship('permission', backref='category')
    class Config:
        orm_mode=True