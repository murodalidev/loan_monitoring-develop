from app.db.connect_db import Base
from sqlalchemy import String, Integer, Column, Integer, Text
from sqlalchemy.orm import relationship

class ProblemsMibType(Base):
    __tablename__='problems_mib_type'
    id=Column(Integer, primary_key=True)
    name = Column(Text, nullable = True)
    code = Column(String(30), nullable = True)
    mib = relationship('ProblemsMib', backref='type')
    class Config:
        orm_mode=True