from app.db.connect_db import Base
from sqlalchemy import String, Integer, Column, Integer, ForeignKey, DateTime, Table, Boolean
from sqlalchemy.orm import relationship



class ProblemsAuctionFiles(Base):
    __tablename__='problems_auction_files'
    id = Column(Integer, primary_key=True)
    problems_auction_id = Column(Integer, ForeignKey('problems_auction.id'), nullable = True, index=True)
    file_url = Column(String(100))
    is_correct = Column(Boolean, default=True)
    is_changed = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=True)
    auction = relationship('ProblemsAuction', backref='files')