from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class TargetMonitoringResult(Base):
    __tablename__='target_monitoring_result'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    code = Column(Integer, nullable=True)
    target_monitoring = relationship('TargetMonitoring', backref='result')
    scheduled_monitoring = relationship('ScheduledMonitoring', backref='result')
    unscheduled_monitoring = relationship('UnscheduledMonitoring', backref='result')
    class Config:
        orm_mode=True