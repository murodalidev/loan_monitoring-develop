from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class LetterStatus(Base):
    __tablename__='letter_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    hybrid_letter = relationship('HybridLetters', backref='status')
    non_target_letter = relationship('NonTargetLetters', backref='status')
    class Config:
        orm_mode=True