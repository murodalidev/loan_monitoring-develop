from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey
from .directory_interface import DirectoryInterface
from sqlalchemy.orm import relationship



class bank_mfo(Base, DirectoryInterface):
    __tablename__='bank_mfo'
    id=Column(Integer, primary_key=True)
    code = Column(String(20), nullable=True)
    name = Column(String(255))
    region_id = Column(Integer, ForeignKey('client_region.id'), nullable=True)
    class Config:
        orm_mode=True
        
        