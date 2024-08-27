from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class MonitoringNotificationType(Base):
    __tablename__='monitoring_notification_type'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    notification = relationship('MonitoringNotification', backref='type')
    class Config:
        orm_mode=True