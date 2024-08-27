from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Text, JSON, Table
from sqlalchemy.orm import relationship

scheduled_extension_files = Table('scheduled_extension_files', Base.metadata,
    Column('scheduled_deadline_extension_history_id', Integer(), ForeignKey("scheduled_deadline_extension_history.id")),
    Column('monitoring_files_id', Integer(), ForeignKey("monitoring_files.id"))
)

class ScheduledDeadlineExtensionMonitoringHistory(Base):
    __tablename__='scheduled_deadline_extension_history'
    id=Column(Integer, primary_key=True)
    scheduled_monitoring_id = Column(Integer, ForeignKey('scheduled_monitoring.id'), nullable = True, index = True)
    type_id = Column(Integer, ForeignKey('case_history_type.id'), nullable = True)
    from_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    from_user = relationship("Users", foreign_keys="ScheduledDeadlineExtensionMonitoringHistory.from_user_id")
    to_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    to_user = relationship("Users", foreign_keys="ScheduledDeadlineExtensionMonitoringHistory.to_user_id")
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    comment = Column(Text, nullable=True)
    message = Column(Text, nullable=True)
    additional_data = Column(JSON, nullable=True)
    files = relationship('MonitoringFiles', secondary=scheduled_extension_files, back_populates='scheduled_extension', overlaps="schedul")
    class Config:
        orm_mode=True
        



target_extension_files = Table('target_extension_files', Base.metadata,
    Column('target_deadline_extension_history_id', Integer(), ForeignKey("target_deadline_extension_history.id")),
    Column('monitoring_files_id', Integer(), ForeignKey("monitoring_files.id"))
)


    
        
class TargetDeadlineExtensionMonitoringHistory(Base):
    __tablename__='target_deadline_extension_history'
    id=Column(Integer, primary_key=True)
    target_monitoring_id = Column(Integer, ForeignKey('target_monitoring.id'), nullable = True, index = True)
    type_id = Column(Integer, ForeignKey('case_history_type.id'), nullable = True)
    from_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    from_user = relationship("Users", foreign_keys="TargetDeadlineExtensionMonitoringHistory.from_user_id")
    to_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    to_user = relationship("Users", foreign_keys="TargetDeadlineExtensionMonitoringHistory.to_user_id")
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    comment = Column(Text, nullable=True)
    message = Column(Text, nullable=True)
    additional_data = Column(JSON, nullable=True)
    files = relationship('MonitoringFiles', secondary=target_extension_files, back_populates='target_extension', overlaps="target")
    class Config:
        orm_mode=True
        
        
        
        
unscheduled_extension_files = Table('unscheduled_extension_files', Base.metadata,
    Column('unscheduled_deadline_extension_history_id', Integer(), ForeignKey("unscheduled_deadline_extension_history.id")),
    Column('monitoring_files_id', Integer(), ForeignKey("monitoring_files.id"))
)


    
        
class UnscheduledDeadlineExtensionMonitoringHistory(Base):
    __tablename__='unscheduled_deadline_extension_history'
    id=Column(Integer, primary_key=True)
    unscheduled_monitoring_id = Column(Integer, ForeignKey('unscheduled_monitoring.id'), nullable = True, index = True)
    type_id = Column(Integer, ForeignKey('case_history_type.id'), nullable = True)
    from_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    from_user = relationship("Users", foreign_keys="UnscheduledDeadlineExtensionMonitoringHistory.from_user_id")
    to_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    to_user = relationship("Users", foreign_keys="UnscheduledDeadlineExtensionMonitoringHistory.to_user_id")
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    comment = Column(Text, nullable=True)
    message = Column(Text, nullable=True)
    additional_data = Column(JSON, nullable=True)
    files = relationship('MonitoringFiles', secondary=unscheduled_extension_files, back_populates='unscheduled_extension', overlaps="unscheduled")
    class Config:
        orm_mode=True