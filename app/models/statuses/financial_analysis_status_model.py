from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class FinancialAnalysisStatus(Base):
    __tablename__='financial_analysis_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    code = Column(Integer, nullable=True)
    financial_analise = relationship('FinancialAnalysis', backref='status')
    scheduled_monitoring = relationship('ScheduledMonitoring', backref='project_status')
    class Config:
        orm_mode=True