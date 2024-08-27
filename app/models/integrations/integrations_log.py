from app.db.connect_db import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship





class Integrations_log(Base):
    __tablename__='integrations_log'
    id = Column(Integer, primary_key=True)
    loan_portfolio_id = Column(Integer, ForeignKey('loan_portfolio.id'), nullable = True, index=True)
    service_id = Column(Integer, ForeignKey('integrations_service.id'), nullable = True, index=True)
    service_api_id = Column(Integer, ForeignKey('integrations_service_api.id'), nullable = True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    api = Column(String(200))
    request = Column(JSON)
    response = Column(JSON)
    created_at = Column(DateTime, nullable=True)
    user = relationship('Users', backref='integration_log')