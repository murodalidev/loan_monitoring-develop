from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Boolean, Text, Table
from sqlalchemy.orm import relationship



class HybridLetters(Base):
    __tablename__='hybrid_letters'
    id=Column(Integer, primary_key=True)
    general_task_id = Column(Integer, ForeignKey('general_tasks.id'), nullable = True)
    letter_receiver_type_id = Column(Integer, ForeignKey('letter_receiver_type.id'), nullable = True)
    is_repaid = Column(Boolean, default=False)
    post_id = Column(String(20), nullable = True)
    letter_post_id = Column(String(20), nullable = True)
    letter_barcode = Column(String(20), nullable = True)
    kad_case_id = Column(Integer, ForeignKey('kad_case.id'), nullable = True)
    letter_status_id = Column(Integer, ForeignKey('letter_status.id'), nullable = True)
    letter_base64 = Column(Text)
    task_manager_id = Column(Integer, ForeignKey('task_manager.id'), nullable=True, index=True)
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