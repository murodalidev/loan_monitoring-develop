from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Table, Date
from sqlalchemy.orm import relationship



class ScheduledMonitoringExpiration(Base):
    __tablename__='scheduled_monitoring_expiration'
    id=Column(Integer, primary_key=True)
    scheduled_monitoring_id = Column(Integer, ForeignKey('scheduled_monitoring.id'), nullable = True)
    responsible_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    deadline_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(Date, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config: 
        orm_mode=True