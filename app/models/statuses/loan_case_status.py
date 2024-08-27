from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class LoanCaseStatus(Base):
    __tablename__='loan_case_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    loan_case = relationship('LoanCase', backref='status')
    class Config:
        orm_mode=True