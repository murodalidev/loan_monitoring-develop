from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Text, JSON, Table
from sqlalchemy.orm import relationship



class BusinessCaseHistory(Base):
    __tablename__='business_case_history'
    id=Column(Integer, primary_key=True)
    business_case_id = Column(Integer, ForeignKey('business_case.id'), nullable = True, index = True)
    general_task_id = Column(Integer, ForeignKey('general_tasks.id'), nullable = True)
    type_id = Column(Integer, ForeignKey('case_history_type.id'), nullable = True)
    from_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    from_user = relationship("Users", foreign_keys="BusinessCaseHistory.from_user_id")
    to_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    to_user = relationship("Users", foreign_keys="BusinessCaseHistory.to_user_id")
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    comment = Column(Text, nullable=True)
    message = Column(Text, nullable=True)
    additional_data = Column(JSON, nullable=True)
    business_case = relationship('BusinessCase', backref='history')
    class Config:
        orm_mode=True