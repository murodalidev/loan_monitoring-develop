from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class TaskStatus(Base):
    __tablename__='task_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    code = Column(Integer, nullable=True)
    task_manager = relationship('TaskManager', backref='status')
    class Config:
        orm_mode=True