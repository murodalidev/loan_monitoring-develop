from app.db.connect_db import Base
from sqlalchemy import String, Integer, Column, Integer, ForeignKey, DateTime, Table, Boolean, Text
from sqlalchemy.orm import relationship

class JudicialAuthority(Base):
    __tablename__='judicial_authority'
    id=Column(Integer, primary_key=True)
    region_id = Column(Integer, ForeignKey('client_region.id'), nullable = True)
    type_id = Column(Integer, ForeignKey('judicial_authority_type.id'), nullable = True)
    name = Column(Text, nullable = True)
    code = Column(Integer, nullable = True)
    judicial_data = relationship('JudicialData', backref='authority')
    class Config:
        orm_mode=True