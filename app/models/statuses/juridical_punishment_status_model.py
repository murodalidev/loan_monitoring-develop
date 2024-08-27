from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class JuridicalPunishmentStatus(Base):
    __tablename__='juridical_punishment_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    juridical_punishment = relationship('JuridicalPunishment', backref='status')
    class Config:
        orm_mode=True