from app.db.connect_db import Base
from sqlalchemy import Integer,Column, Column, Integer, ForeignKey, DateTime, String, Boolean, Table, BigInteger, Date
from sqlalchemy.orm import relationship


class LoanPortfolioSchedule(Base):
    __tablename__='loan_portfolio_schedule'
    id=Column(Integer, primary_key=True)
    loan_id=Column(BigInteger, nullable = True, index=True)
    uuid = Column(Integer, index=True)
    date_red = Column(DateTime, nullable=True)
    summ_red = Column(String(30), nullable=True)
    sign_long = Column(String(30), nullable=True)
    condition = Column(String(30), nullable=True)
    date_modify = Column(DateTime, nullable=True)
    created = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    
    class Config:
        orm_mode=True
        