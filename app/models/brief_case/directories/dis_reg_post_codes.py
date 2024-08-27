from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship




class post_codes(Base):
    __tablename__='post_codes'
    id=Column(Integer, primary_key=True)
    dist_code_post = Column(Integer, nullable=True)
    reg_code_post = Column(Integer, nullable=True)
    dist_code_iabs = Column(Integer, nullable=True)
    dist_name_iabs = Column(String(30), nullable=True)
    class Config:
        orm_mode=True