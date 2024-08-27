from app.db.connect_db import Base
from sqlalchemy import String, Integer, Column, Integer, ForeignKey, DateTime, Table, Boolean, Text
from sqlalchemy.orm import relationship

class JudicialAuthorityType(Base):
    __tablename__='judicial_authority_type'
    id=Column(Integer, primary_key=True)
    name = Column(Text, nullable = True)
    name_full = Column(Text, nullable = True)
    code = Column(Integer, nullable = True)
    judicial_data = relationship('JudicialAuthority', backref='type')
    class Config:
        orm_mode=True