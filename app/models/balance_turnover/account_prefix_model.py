from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey

from sqlalchemy.orm import relationship



class AccountPrefix(Base):
    __tablename__='account_prefix'
    id=Column(Integer, primary_key=True)
    code = Column(String(10), nullable=True)
    name = Column(String(50), nullable=True)
    class Config:
        orm_mode=True
        
        