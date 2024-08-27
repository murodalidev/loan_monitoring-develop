from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class ReportOrderStatus(Base):
    __tablename__='report_order_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    code = Column(Integer, nullable=True)
    report_roder = relationship('ReportOrder', backref='report_status')
    class Config:
        orm_mode=True
        
        
        
        
class ReportOrderType(Base):
    __tablename__='report_order_type'
    id=Column(Integer, primary_key=True)
    name = Column(String(20))
    code = Column(Integer, nullable=True)
    report_roder = relationship('ReportOrder', backref='report_type')
    class Config:
        orm_mode=True
        
        


class ReportBy(Base):
    __tablename__='report_by'
    id=Column(Integer, primary_key=True)
    name = Column(String(20))
    code = Column(Integer, nullable=True)
    report_by = relationship('ReportOrder', backref='report_by')
    class Config:
        orm_mode=True