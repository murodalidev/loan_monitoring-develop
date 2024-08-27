from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Text, JSON, Table
from sqlalchemy.orm import relationship


class UnscheduledMonitoringHistory(Base):
    __tablename__='unscheduled_monitoring_history'
    id=Column(Integer, primary_key=True)
    monitoring_case_id = Column(Integer, ForeignKey('monitoring_case.id'), nullable = True)
    type_id = Column(Integer, ForeignKey('case_history_type.id'), nullable = True)
    from_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    from_user = relationship("Users", foreign_keys="UnscheduledMonitoringHistory.from_user_id")
    to_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    to_user = relationship("Users", foreign_keys="UnscheduledMonitoringHistory.to_user_id")
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    comment = Column(Text, nullable=True)
    message = Column(Text, nullable=True)
    additional_data = Column(JSON, nullable=True)
    
    class Config:
        orm_mode=True