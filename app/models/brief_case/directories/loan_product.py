from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship




class loan_product(Base):
    __tablename__='loan_product'
    id=Column(Integer, primary_key=True)
    name = Column(Text)
    type = Column(Integer, ForeignKey('loan_product_type.id'), nullable=True)
    is_target = Column(Integer, nullable=True)
    checked = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True
        
        
        



class loan_product_edit(Base):
    __tablename__='loan_product_edit'
    id=Column(Integer, primary_key=True)
    name_old = Column(Text, nullable=True)
    name_new = Column(Text, nullable=True)
    type_old = Column(Integer, nullable=True)
    type_new = Column(Integer, nullable=True)
    is_target_old = Column(Integer, nullable=True)
    is_target_new = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True