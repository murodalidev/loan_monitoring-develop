from app.db.connect_db import Base
from sqlalchemy import String, Integer, Column, Integer, Text
from sqlalchemy.orm import relationship

class NonTargetType(Base):
    __tablename__='non_target_type'
    id=Column(Integer, primary_key=True)
    name = Column(Text, nullable = True)
    code = Column(String(30), nullable = True)
    non_target = relationship('NonTargetState', backref='type')
    class Config:
        orm_mode=True