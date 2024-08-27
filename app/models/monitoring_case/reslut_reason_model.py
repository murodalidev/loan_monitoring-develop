from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, Text
from sqlalchemy.orm import relationship



class ResultReason(Base):
    __tablename__='result_reason'
    id=Column(Integer, primary_key=True)
    name = Column(Text)
    code = Column(Integer, nullable=True)
    target_monitoring = relationship('TargetMonitoring', backref='reason')
    scheduled_monitoring = relationship('ScheduledMonitoring', backref='reason')
    unscheduled_monitoring = relationship('UnscheduledMonitoring', backref='reason')
    class Config:
        orm_mode=True