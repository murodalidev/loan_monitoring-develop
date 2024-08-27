from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class LetterReceiverType(Base):
    __tablename__='letter_receiver_type'
    id=Column(Integer, primary_key=True)
    name = Column(String(20))
    hybrid_letter = relationship('HybridLetters', backref='receiver_type')
    class Config:
        orm_mode=True