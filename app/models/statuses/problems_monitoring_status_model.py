from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class ProblemsMonitoringStatus(Base):
    __tablename__='problems_monitoring_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    code = Column(Integer, nullable=True)
    #problems_monitoring = relationship('ProblemsMonitoring', backref='status')
    class Config:
        orm_mode=True