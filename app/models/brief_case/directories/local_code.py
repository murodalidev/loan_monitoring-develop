from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship




class local_code(Base):
    __tablename__='local_code'
    id=Column(Integer, primary_key=True)
    code = Column(String(20), nullable=True)
    name = Column(String(255))
    region_id = Column(Integer, ForeignKey('client_region.id'), nullable=True)
    head = Column(Integer, ForeignKey('local_code.id'), nullable=True)
    index = Column(String(15), nullable=True)
    address =  Column(Text, nullable=True)
    inn = Column(String(20), nullable=True)
    phone_number = Column(String(20), nullable=True)
    manager = Column(String(50), nullable=True)
    status = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    heads = relationship('local_code', backref='sub', remote_side=[id])
    attached = relationship('attached_branches', backref='local_code')
    portfolio = relationship('Loan_Portfolio', backref='local_code')
    employee = relationship('Users', backref='local')
    class Config:
        orm_mode=True
        
        
        
        
        


class local_code_edit(Base):
    __tablename__='local_code_edit'
    id=Column(Integer, primary_key=True)
    code_old = Column(String(20), nullable=True)
    code_new = Column(String(20), nullable=True)
    name_old = Column(String(255), nullable=True)
    name_new = Column(String(255), nullable=True)
    region_old = Column(Integer, nullable=True)
    region_new = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True