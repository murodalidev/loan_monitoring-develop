from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship



class TaskManagerComments(Base):
    __tablename__='task_manager_comments'
    id=Column(Integer, primary_key=True)
    task_manager_id = Column(Integer, ForeignKey('task_manager.id'))
    from_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    from_user = relationship("Users", foreign_keys="TaskManagerComments.from_user_id")
    to_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    to_user = relationship("Users", foreign_keys="TaskManagerComments.to_user_id")
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    task_manager = relationship('TaskManager', backref='comments')
    
    class Config:
        orm_mode=True