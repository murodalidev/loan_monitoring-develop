from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship




class loan_product_type(Base):
    __tablename__='loan_product_type'
    id=Column(Integer, primary_key=True)
    name = Column(String(20))
    loan_product = relationship('loan_product', backref='loan_type')
    class Config:
        orm_mode=True