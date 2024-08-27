from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class KADMonitoringResult(Base):
    __tablename__='kad_monitoring_result'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    kad_monitoring = relationship('KADMonitoring', backref='result')
    class Config:
        orm_mode=True