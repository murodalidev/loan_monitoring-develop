from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship



class Departments(Base):
    __tablename__='departments'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    region_id = Column(Integer, ForeignKey('client_region.id'), nullable = True)
    user = relationship('Users', backref='depart')
    class Config:
        orm_mode=True