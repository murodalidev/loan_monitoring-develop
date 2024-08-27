from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Boolean, Text, Table
from sqlalchemy.orm import relationship



class NonTargetLetters(Base):
    __tablename__='non_target_letters'
    id=Column(Integer, primary_key=True)
    problems_case_id = Column(Integer, ForeignKey('problems_case.id'), nullable = True)
    letter_receiver_type_id = Column(Integer, ForeignKey('letter_receiver_type.id'), nullable = True)
    post_id = Column(String(20), nullable = True)
    letter_post_id = Column(String(20), nullable = True)
    letter_status_id = Column(Integer, ForeignKey('letter_status.id'), nullable = True)
    letter_url = Column(String(100), nullable=True)
    perform = Column(String(100), nullable=True)
    perform_date_time = Column(DateTime, nullable=True)
    perform_date_time_str = Column(String(100), nullable=True)
    perform_update_date_time = Column(DateTime, nullable=True)
    perform_update_date_time_str = Column(String(100), nullable=True)
    note = Column(String(100), nullable=True)
    error_comment =Column(String(100), nullable=True)
    courier = Column(String(100), nullable=True)
    post_index = Column(String(100), nullable=True)
    send_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    
    class Config:
        orm_mode=True