from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship



class ProblemsStateNotification(Base):
    __tablename__='problems_state_notification'
    id=Column(Integer, primary_key=True)
    loan_portfolio_id = Column(Integer, ForeignKey('loan_portfolio.id'), nullable = True, index=True)
    judicial_status_id = Column(Integer, ForeignKey('problems_assets_status.id'), nullable = True)
    problems_assets_get_status_id = Column(Integer, ForeignKey('problems_assets_status.id'))
    problems_assets_sell_status_id = Column(Integer, ForeignKey('problems_assets_status.id'))
    out_of_balance_status_id = Column(Integer, ForeignKey('problems_assets_status.id'))
    letter_35_status_id = Column(Boolean, default=False)
    letter_45_status_id = Column(Boolean, default=False)
    bpi_status = Column(Boolean, default=False)
    bpi_ended_status = Column(Integer, ForeignKey('problems_assets_status.id'))
    auction_status = Column(Integer, ForeignKey('problems_assets_status.id'))
    tpp_status = Column(Boolean, default=False)
    class Config:
        orm_mode=True