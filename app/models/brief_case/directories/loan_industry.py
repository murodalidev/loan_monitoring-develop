from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer





class loan_industry(Base):
    __tablename__='loan_industry'
    id=Column(Integer, primary_key=True)
    code = Column(String(20), nullable=True)
    name = Column(String(255))
    class Config:
        orm_mode=True