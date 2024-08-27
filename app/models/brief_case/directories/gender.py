from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship




class gender(Base):
    __tablename__='gender'
    id=Column(Integer, primary_key=True)
    code = Column(String(20), nullable=True)
    name = Column(String(255))
    loan_portfolio = relationship('Loan_Portfolio', backref='gender')
    class Config:
        orm_mode=True