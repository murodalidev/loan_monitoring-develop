from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Table, Date
from sqlalchemy.orm import relationship



class UnscheduledMonitoringExpiration(Base):
    __tablename__='unscheduled_monitoring_expiration'
    id=Column(Integer, primary_key=True)
    unscheduled_monitoring_id = Column(Integer, ForeignKey('unscheduled_monitoring.id'), nullable = True)
    responsible_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    deadline_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(Date, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config: 
        orm_mode=True