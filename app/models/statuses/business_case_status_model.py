from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class BusinessCaseStatus(Base):
    __tablename__='business_case_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    business_case = relationship('BusinessCase', backref='status')
    class Config:
        orm_mode=True