from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship



class GeneralTasks(Base):
    __tablename__='general_tasks'
    id=Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    category_id = Column(Integer, ForeignKey('general_tasks_category.id'))
    level = Column(Integer, nullable=True)
    task_manager = relationship('TaskManager', backref='general_task')
    hybrid_letters = relationship('HybridLetters', backref='general_task')
    loan_history = relationship('LoanCaseHistory', backref='general_task')
    class Config:
        orm_mode=True