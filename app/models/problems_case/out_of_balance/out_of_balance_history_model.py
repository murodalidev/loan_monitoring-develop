from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Text, JSON, Table
from sqlalchemy.orm import relationship




class OutOfBalanceHistory(Base):
    __tablename__='out_of_balance_history'
    id=Column(Integer, primary_key=True)
    problems_case_id = Column(Integer, ForeignKey('problems_case.id'), nullable = True)
    from_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    from_user = relationship("Users", foreign_keys="OutOfBalanceHistory.from_user_id")
    to_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    to_user = relationship("Users", foreign_keys="OutOfBalanceHistory.to_user_id")
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    comment = Column(Text, nullable=True)
    message = Column(Text, nullable=True)
    additional_data = Column(JSON, nullable=True)
    class Config:
        orm_mode=True