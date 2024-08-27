from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Boolean, Text, Table
from sqlalchemy.orm import relationship



class ReportOrder(Base):
    __tablename__='report_order'
    id=Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    path = Column(String(60), nullable=True)
    type = Column(Integer, ForeignKey('report_order_type.id'), nullable = True)
    report_by_id = Column(Integer, ForeignKey('report_by.id'), nullable = True)
    status = Column(Integer, ForeignKey('report_order_status.id'), nullable = True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True