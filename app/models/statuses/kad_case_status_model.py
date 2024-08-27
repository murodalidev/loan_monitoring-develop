from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class KADCaseStatus(Base):
    __tablename__='kad_case_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    kad_case = relationship('KADCase', backref='status')
    class Config:
        orm_mode=True