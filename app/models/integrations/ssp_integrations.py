from app.db.connect_db import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Table, Text, Numeric, String
from sqlalchemy.orm import relationship





class SSP_integrations(Base):
    __tablename__='ssp_integrations'
    id = Column(Integer, primary_key=True)
    loan_portfolio_id = Column(Integer, ForeignKey('loan_portfolio.id'), nullable = True, index=True)
    request_id = Column(Integer)
    contractIdentificationNumber = Column(String(30))
    claimThemeId = Column(Integer)
    claimResponsibleTypeId = Column(Integer)
    claimApplicationTypeId = Column(Integer)
    mainDebt = Column(Numeric(15,2))
    calculedPenalty = Column(Numeric(15,2))
    penalty = Column(Numeric(15,2))
    percent = Column(Numeric(15,2))
    currentPrincipalInterest = Column(Numeric(15,2))
    currentInterestRate = Column(Numeric(15,2))
    otherDebtRepayment = Column(Numeric(15,2))
    currencyId = Column(Integer)
    details = Column(Text)
    fileAsBase64 = Column(Text)
    created_at = Column(DateTime, nullable=True)
    files = relationship('SSPFiles', backref='ssp')
    



class SSPFiles(Base):
    __tablename__='ssp_files'
    id = Column(Integer, primary_key=True)
    ssp_id = Column(Integer, ForeignKey('ssp_integrations.id'), nullable = True, index=True)
    file_url = Column(String(100))
    created_at = Column(DateTime, nullable=True)