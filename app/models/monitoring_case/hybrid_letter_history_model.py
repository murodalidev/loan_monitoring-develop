from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Table, Date
from sqlalchemy.orm import relationship



class HybridLetterHistory(Base):
    __tablename__='hybrid_letter_history'
    id=Column(Integer, primary_key=True)
    monitoring_case_id = Column(Integer, ForeignKey('monitoring_case.id'), nullable = True)
    scheduled_monitoring_status_id = Column(Integer, ForeignKey('scheduled_monitoring_status.id'), nullable = True)
    scheduled_monitoring_result_id = Column(Integer, ForeignKey('target_monitoring_result.id'), nullable = True)
    frequency_period_id = Column(Integer, ForeignKey('monitoring_frequency_period.id'), nullable = True)
    task_manager_id = Column(Integer, ForeignKey('task_manager.id'), nullable=True, index=True)
    main_responsible_due_date = Column(DateTime, nullable=True)
    second_responsible_due_date = Column(DateTime, nullable=True)
    created_at = Column(Date, nullable=True)
    deadline = Column(Date, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    scheduled_expiration = relationship('ScheduledMonitoringExpiration', backref='scheduled')
    class Config: 
        orm_mode=True