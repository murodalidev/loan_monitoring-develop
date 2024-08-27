from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Table, Date, Text
from sqlalchemy.orm import relationship


scheduled_monitoring_files = Table('scheduled_monitoring_files', Base.metadata,
    Column('scheduled_monitoring_id', Integer(), ForeignKey("scheduled_monitoring.id")),
    Column('monitoring_files_id', Integer(), ForeignKey("monitoring_files.id"))
)





class ScheduledMonitoring(Base):
    __tablename__='scheduled_monitoring'
    id=Column(Integer, primary_key=True)
    monitoring_case_id = Column(Integer, ForeignKey('monitoring_case.id'), nullable = True)
    scheduled_monitoring_status_id = Column(Integer, ForeignKey('monitoring_status.id'), nullable = True)
    scheduled_monitoring_result_id = Column(Integer, ForeignKey('target_monitoring_result.id'), nullable = True)
    scheduled_monitoring_result_reason_id = Column(Integer, ForeignKey('result_reason.id'), nullable = True)
    scheduled_monitoring_result_reason_comment = Column(Text, nullable = True)
    amount=Column(String(20))
    frequency_period_id = Column(Integer, ForeignKey('monitoring_frequency_period.id'), nullable = True)
    task_manager_id = Column(Integer, ForeignKey('task_manager.id'), nullable=True, index=True)
    project_status_id = Column(Integer, ForeignKey("financial_analysis_status.id"), nullable = True)
    main_responsible_due_date = Column(DateTime, nullable=True)
    second_responsible_due_date = Column(DateTime, nullable=True)
    created_at = Column(Date, nullable=True)
    deadline = Column(Date, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    scheduled_expiration = relationship('ScheduledMonitoringExpiration', backref='scheduled')
    files = relationship('MonitoringFiles', secondary=scheduled_monitoring_files, back_populates='scheduled_monitoring', overlaps="schedule")
    class Config: 
        orm_mode=True