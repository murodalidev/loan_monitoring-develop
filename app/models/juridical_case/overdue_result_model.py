from app.db.connect_db import Base
from sqlalchemy import Integer,Column, Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship



class OverdueResult(Base):
    __tablename__='overdue_result'
    id=Column(Integer, primary_key=True)
    name = Column(String(20), nullable=True)
    juridical_intended = relationship('JuridicalIntendedOverdue', backref='result')
    class Config:
        orm_mode=True