from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Table, Text
from sqlalchemy.orm import relationship


target_monitoring_files = Table('target_monitoring_files', Base.metadata,
    Column('target_monitoring_id', Integer(), ForeignKey("target_monitoring.id")),
    Column('monitoring_files_id', Integer(), ForeignKey("monitoring_files.id"))
)




class TargetMonitoring(Base):
    __tablename__='target_monitoring'
    id=Column(Integer, primary_key=True)
    target_monitoring_status_id = Column(Integer, ForeignKey('monitoring_status.id'), nullable = True)
    target_monitoring_result_id = Column(Integer, ForeignKey('target_monitoring_result.id'), nullable = True)
    target_monitoring_result_reason_id = Column(Integer, ForeignKey('result_reason.id'), nullable = True)
    target_monitoring_result_reason_comment = Column(Text, nullable = True)
    task_manager_id = Column(Integer, ForeignKey('task_manager.id'), nullable=True, index=True)
    amount=Column(String(20))
    deadline = Column(DateTime, nullable=True)
    main_responsible_due_date = Column(DateTime, nullable=True)
    second_responsible_due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    target_expiration = relationship('TargetMonitoringExpiration', backref='target')
    monitoring_case = relationship('MonitoringCase', backref='target')
    target_history = relationship('TargetMonitoringHistory', backref='target_monitoring')
    files = relationship('MonitoringFiles', secondary=target_monitoring_files, back_populates='target_monitoring', overlaps="target")
    
    class Config: 
        orm_mode=True