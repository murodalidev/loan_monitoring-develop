from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class ScheduledMonitoringStatus(Base):
    __tablename__='scheduled_monitoring_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    code = Column(Integer, nullable=True)
    class Config:
        orm_mode=True