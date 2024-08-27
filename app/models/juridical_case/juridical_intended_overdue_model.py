from app.db.connect_db import Base
from sqlalchemy import Integer,Column, Column, Integer, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship





class JuridicalIntendedOverdue(Base):
    __tablename__='juridical_intended_overdue'
    id=Column(Integer, primary_key=True)
    juridical_case_id = Column(Integer, ForeignKey('juridical_case.id'), nullable=True, index=True)
    juridical_type_id = Column(Integer, ForeignKey('general_tasks.id'), nullable=True)
    overdue_result = Column(Integer, ForeignKey('overdue_result.id'), nullable=True)
    task_manager_id = Column(Integer, ForeignKey('task_manager.id'), nullable=True, index=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True