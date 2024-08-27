from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class JuridicalCaseStatus(Base):
    __tablename__='juridical_case_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(50), nullable=True)
    code = Column(Integer, nullable=True)
    juridical_punishment = relationship('JuridicalCase', backref='status')
    class Config:
        orm_mode=True