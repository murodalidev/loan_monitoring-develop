from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class ProblemsCaseStatus(Base):
    __tablename__='problems_case_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    code = Column(Integer, nullable=True)
    problems_monitoring = relationship('ProblemsCase', backref='status')
    class Config:
        orm_mode=True