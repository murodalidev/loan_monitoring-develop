from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Table, Date, Text
from sqlalchemy.orm import relationship


unscheduled_monitoring_files = Table('unscheduled_monitoring_files', Base.metadata,
    Column('unscheduled_monitoring_id', Integer(), ForeignKey("unscheduled_monitoring.id")),
    Column('monitoring_files_id', Integer(), ForeignKey("monitoring_files.id"))
)





class UnscheduledMonitoring(Base):
    __tablename__='unscheduled_monitoring'
    id=Column(Integer, primary_key=True)
    monitoring_case_id = Column(Integer, ForeignKey('monitoring_case.id'), nullable = True)
    unscheduled_monitoring_status_id = Column(Integer, ForeignKey('monitoring_status.id'), nullable = True)
    unscheduled_monitoring_result_id = Column(Integer, ForeignKey('target_monitoring_result.id'), nullable = True)
    unscheduled_monitoring_result_reason_id = Column(Integer, ForeignKey('result_reason.id'), nullable = True)
    unscheduled_monitoring_result_reason_comment = Column(Text, nullable = True)
    project_status_id = Column(Integer, ForeignKey("financial_analysis_status.id"), nullable = True)
    amount=Column(String(20))
    task_manager_id = Column(Integer, ForeignKey('task_manager.id'), nullable=True, index=True)
    main_responsible_due_date = Column(DateTime, nullable=True)
    second_responsible_due_date = Column(DateTime, nullable=True)
    deadline = Column(Date, nullable=True)
    created_at = Column(Date, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    unscheduled_expiration = relationship('UnscheduledMonitoringExpiration', backref='unscheduled')
    files = relationship('MonitoringFiles', secondary=unscheduled_monitoring_files, back_populates='unscheduled_monitoring', overlaps="unschedule")
    class Config: 
        orm_mode=True