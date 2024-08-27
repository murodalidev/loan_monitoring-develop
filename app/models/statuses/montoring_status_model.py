from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class MonitoringStatus(Base):
    __tablename__='monitoring_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    code = Column(Integer, nullable=True)
    target_monitoring = relationship('TargetMonitoring', backref='status')
    scheduled_monitoring = relationship('ScheduledMonitoring', backref='status')
    unscheduled_monitoring = relationship('UnscheduledMonitoring', backref='status')
    problems_monitoring = relationship('ProblemsMonitoring', backref='status')
    
    class Config:
        orm_mode=True