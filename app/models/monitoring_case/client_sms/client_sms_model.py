from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Table, Date, Boolean
from sqlalchemy.orm import relationship



class ClientSms(Base):
    __tablename__='client_sms'
    id=Column(Integer, primary_key=True)
    loan_id = Column(Integer, ForeignKey('loan_portfolio.loan_id'), nullable = True, index=True)
    date_red = Column(Date, nullable=True)
    status = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config: 
        orm_mode=True 