from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class AttachedType(Base):
    __tablename__='attached_type'
    id=Column(Integer, primary_key=True)
    name = Column(String(20))
    code = Column(Integer, nullable=True)
    attached_branches = relationship('attached_branches', backref='type')
    class Config:
        orm_mode=True