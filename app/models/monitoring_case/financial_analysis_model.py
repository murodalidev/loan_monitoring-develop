from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship



class FinancialAnalysis(Base):
    __tablename__='financial_analysis'
    id=Column(Integer, primary_key=True)
    monitoring_case_id = Column(Integer, ForeignKey('monitoring_case.id'), nullable = True)
    income_plan=Column(String(20), nullable = True)
    income_fact=Column(String(20), nullable = True)
    profit_plan=Column(String(20), nullable = True)
    profit_fact=Column(String(20), nullable = True)
    expences_plan=Column(String(20), nullable = True)
    expences_fact=Column(String(20), nullable = True)
    net_profit_plan=Column(String(20), nullable = True)
    net_profit_fact=Column(String(20), nullable = True)
    new_workplaces_plan=Column(String(20), nullable = True)
    new_workplaces_fact=Column(String(20), nullable = True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    financial_analysis_status_id = Column(Integer, ForeignKey("financial_analysis_status.id"), nullable = True)
    year = Column(Integer, nullable=True)
    class Config: 
        orm_mode=True