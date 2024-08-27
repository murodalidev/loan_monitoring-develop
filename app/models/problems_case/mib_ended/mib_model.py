from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Table, Date
from sqlalchemy.orm import relationship



class ProblemsMib(Base):
    __tablename__='problems_mib'
    id=Column(Integer, primary_key=True)
    problems_case_id = Column(Integer, ForeignKey('problems_case.id'), nullable = True)
    mib_ended_status_id = Column(Integer, ForeignKey('problems_assets_status.id'), nullable = True)
    type_id = Column(Integer, ForeignKey('problems_mib_type.id'), nullable = True, index=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config: 
        orm_mode=True