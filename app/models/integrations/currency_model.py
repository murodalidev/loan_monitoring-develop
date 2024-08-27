from app.db.connect_db import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, Date, Float
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
import datetime




class CurrencyRate(Base):
    __tablename__='currency_rate'
    id = Column(Integer, primary_key=True)
    equival = Column(Float)
    name = Column(String(50))
    code = Column(Integer, ForeignKey('currency.id'), nullable = True, index=True)
    request_id = Column(String(50))
    date = Column(Date, default=datetime.datetime.now().date(), nullable=True)