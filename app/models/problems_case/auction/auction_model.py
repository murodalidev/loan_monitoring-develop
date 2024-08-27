from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Table, Date
from sqlalchemy.orm import relationship



class ProblemsAuction(Base):
    __tablename__='problems_auction'
    id=Column(Integer, primary_key=True)
    problems_case_id = Column(Integer, ForeignKey('problems_case.id'), nullable = True)
    auction_status_id = Column(Integer, ForeignKey('problems_assets_status.id'), nullable = True)
    type_id = Column(Integer, ForeignKey('problems_auction_type.id'), nullable = True, index=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config: 
        orm_mode=True