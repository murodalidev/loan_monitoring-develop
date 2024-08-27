from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class MonitoringFrequencyPeriod(Base):
    __tablename__='monitoring_frequency_period'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    code = Column(Integer, nullable=True)
    scheduled_monitoring = relationship('ScheduledMonitoring', backref='frequency_period')
    class Config:
        orm_mode=True