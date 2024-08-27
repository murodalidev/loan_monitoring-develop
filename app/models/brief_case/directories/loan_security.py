from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer





class loan_security(Base):
    __tablename__='loan_security'
    id=Column(Integer, primary_key=True)
    code = Column(String(20), nullable=True)
    name = Column(String(255))
    class Config:
        orm_mode=True