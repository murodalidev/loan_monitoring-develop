from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer




class user_status(Base):
    __tablename__='user_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(30))
    
    class Config:
        orm_mode=True