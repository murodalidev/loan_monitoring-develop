from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class IntendedOverdueType(Base):
    __tablename__='intended_overdue_type'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    juridical_case = relationship('JuridicalCase', backref='type')
    class Config:
        orm_mode=True