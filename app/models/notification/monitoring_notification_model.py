from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship



class MonitoringNotification(Base):
    __tablename__='monitoring_notification'
    id=Column(Integer, primary_key=True)
    from_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    from_user = relationship("Users", foreign_keys="MonitoringNotification.from_user_id")
    to_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    to_user = relationship("Users", foreign_keys="MonitoringNotification.to_user_id")
    notification_type_id = Column(Integer, ForeignKey('monitoring_notification_type.id'), nullable = True)
    is_read = Column(Boolean, default=False)
    body = Column(Text, nullable = True)
    url = Column(String(255), nullable = True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    
    class Config:
        orm_mode=True