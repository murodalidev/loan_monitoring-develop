from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class MonitoringCaseStatus(Base):
    __tablename__='monitoring_case_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    monitoring_case = relationship('MonitoringCase', backref='status')
    class Config:
        orm_mode=True