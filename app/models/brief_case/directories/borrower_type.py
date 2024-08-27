from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from .directory_interface import DirectoryInterface




class borrower_type(Base, DirectoryInterface):
    __tablename__='borrower_type'
    id=Column(Integer, primary_key=True)
    code = Column(String(20), nullable=True)
    name = Column(String(255))
    class Config:
        orm_mode=True