from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Table, Date
from sqlalchemy.orm import relationship



class NonTargetState(Base):
    __tablename__='non_target_state'
    id=Column(Integer, primary_key=True)
    problems_case_id = Column(Integer, ForeignKey('problems_case.id'), nullable = True)
    type_id = Column(Integer, ForeignKey('non_target_type.id'), nullable = True, index=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config: 
        orm_mode=True