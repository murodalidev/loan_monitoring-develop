from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class BusinessMonitoringStatus(Base):
    __tablename__='business_monitoring_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    business_monitoring = relationship('BusinessMonitoring', backref='status')
    class Config:
        orm_mode=True