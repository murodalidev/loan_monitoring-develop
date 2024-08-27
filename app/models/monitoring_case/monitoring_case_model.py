from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship



class MonitoringCase(Base):
    __tablename__='monitoring_case'
    id=Column(Integer, primary_key=True)
    target_monitoring_id = Column(Integer, ForeignKey('target_monitoring.id'), nullable = True)
    monitoring_case_status_id = Column(Integer, ForeignKey('monitoring_case_status.id'), nullable = True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    loan_case = relationship('LoanCase', backref='monitoring_case')
    scheduled_monitoring = relationship('ScheduledMonitoring', backref='monitoring_case')
    unscheduled_monitoring = relationship('UnscheduledMonitoring', backref='monitoring_case')
    scheduled_history = relationship('ScheduledMonitoringHistory', backref='monitoring_case')
    class Config:
        orm_mode=True