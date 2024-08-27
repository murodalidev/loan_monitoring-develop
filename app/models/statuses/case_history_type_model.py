from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class CaseHistoryType(Base):
    __tablename__='case_history_type'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    code = Column(Integer, nullable=True)
    loan_case_history = relationship('LoanCaseHistory', backref='type')
    class Config:
        orm_mode=True