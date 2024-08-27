from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from .directory_interface import DirectoryInterface
from sqlalchemy.orm import relationship



class client_region(Base, DirectoryInterface):
    __tablename__='client_region'
    id=Column(Integer, primary_key=True)
    code = Column(String(20), nullable=True)
    post_code = Column(Integer, nullable=True)
    name = Column(String(255))
    region_codes = Column(String(10))
    loan_portfolio = relationship('Loan_Portfolio', backref='region')
    district = relationship('client_district', backref='region')
    local_code = relationship('local_code', backref='region')
    user = relationship('Users', backref='region')
    department = relationship('Departments', backref='region')
    judicial = relationship('JudicialData', backref='region')
    attached = relationship('attached_regions', backref='region')
    authority = relationship('JudicialAuthority', backref='region')
    class Config:
        orm_mode=True