from app.db.connect_db import Base
from sqlalchemy import String, Integer, Column, Integer, ForeignKey, DateTime, Table, Boolean, Text
from sqlalchemy.orm import relationship

class ProblemsAssetsType(Base):
    __tablename__='problems_assets_type'
    id=Column(Integer, primary_key=True)
    name = Column(String(20), nullable = True)
    name_full = Column(Text, nullable = True)
    code = Column(Integer, nullable = True)
    problems_assets = relationship('ProblemsAssets', backref='type')
    class Config:
        orm_mode=True