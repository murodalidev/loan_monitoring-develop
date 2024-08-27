from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer
from sqlalchemy.orm import relationship



class ProblemsAssetsStatus(Base):
    __tablename__='problems_assets_status'
    id=Column(Integer, primary_key=True)
    name = Column(String(50))
    problems_assets = relationship('ProblemsAssets', backref='status')
    out_of_balance = relationship('OutOfBalance', backref='status')
    judicial_data = relationship('JudicialData', backref='status')
    class Config:
        orm_mode=True