from app.db.connect_db import Base
from sqlalchemy import String, Integer, Column, Integer, ForeignKey, DateTime, Table, Boolean, Text
from sqlalchemy.orm import relationship

class JudicialType(Base):
    __tablename__='judicial_type'
    id=Column(Integer, primary_key=True)
    name = Column(Text, nullable = True)
    name_full = Column(Text, nullable = True)
    code = Column(Integer, nullable = True)
    judcial_data = relationship('JudicialData', backref='type')
    class Config:
        orm_mode=True