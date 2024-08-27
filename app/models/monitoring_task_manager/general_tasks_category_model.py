from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship



class GeneralTasksCategory(Base):
    __tablename__='general_tasks_category'
    id=Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    general_task = relationship('GeneralTasks', backref='category')
    
    class Config:
        orm_mode=True