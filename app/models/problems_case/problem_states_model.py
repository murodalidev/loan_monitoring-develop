from app.db.connect_db import Base
from sqlalchemy import String, Integer, Column, Integer, ForeignKey, DateTime, Table, Boolean


class ProblemStates(Base):
    __tablename__='problem_states'
    id=Column(Integer, primary_key=True)
    name = Column(String(20), nullable = True)
    code = Column(Integer, nullable = True)
    class Config:
        orm_mode=True