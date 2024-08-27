from app.db.connect_db import Base
from sqlalchemy import String, Integer, Column, Integer, ForeignKey, DateTime, Table, Boolean, BigInteger
from sqlalchemy.orm import relationship

class ProblemStateChain(Base):
    __tablename__='problem_state_chain'
    id=Column(Integer, primary_key=True)
    loan_id = Column(BigInteger, nullable=True, index=True)
    
    letter_35_id = Column(Integer, ForeignKey('problem_states.id'), nullable = True)
    letter_35 = relationship("ProblemStates", foreign_keys="ProblemStateChain.letter_35_id")
    letter_35_date = Column(DateTime, nullable = True)
    
    letter_45_id = Column(Integer, ForeignKey('problem_states.id'), nullable = True)
    letter_45 = relationship("ProblemStates", foreign_keys="ProblemStateChain.letter_45_id")
    letter_45_date = Column(DateTime, nullable = True)
    
    ssp_id = Column(Integer, ForeignKey('problem_states.id'), nullable = True)
    ssp = relationship("ProblemStates", foreign_keys="ProblemStateChain.ssp_id")
    ssp_date = Column(DateTime, nullable = True)
    
    judicial_process_id = Column(Integer, ForeignKey('problem_states.id'), nullable = True)
    judicial_process = relationship("ProblemStates", foreign_keys="ProblemStateChain.judicial_process_id")
    judicial_process_date = Column(DateTime, nullable = True)
    
    bpi_id = Column(Integer, ForeignKey('problem_states.id'), nullable = True)
    bpi = relationship("ProblemStates", foreign_keys="ProblemStateChain.bpi_id")
    bpi_date = Column(DateTime, nullable = True)
    
    
    problem_state_id = Column(Integer, ForeignKey('problem_states.id'), nullable = True)
    problem_state = relationship("ProblemStates", foreign_keys="ProblemStateChain.problem_state_id")
    problem_state_date = Column(DateTime, nullable = True)
    
    
    out_of_balance_id = Column(Integer, ForeignKey('problem_states.id'), nullable = True)
    out_of_balance = relationship("ProblemStates", foreign_keys="ProblemStateChain.out_of_balance_id")
    out_of_balance_date = Column(DateTime, nullable = True)
    
    
    auction_id = Column(Integer, ForeignKey('problem_states.id'), nullable = True)
    auction = relationship("ProblemStates", foreign_keys="ProblemStateChain.auction_id")
    auction_date = Column(DateTime, nullable = True)
    
    bpi_ended_id = Column(Integer, ForeignKey('problem_states.id'), nullable = True)
    bpi_ended = relationship("ProblemStates", foreign_keys="ProblemStateChain.bpi_ended_id")
    bpi_ended_date = Column(DateTime, nullable = True)
    
    last_state_id = Column(Integer, ForeignKey('problem_states.id'), nullable = True)
    last_state = relationship("ProblemStates", foreign_keys="ProblemStateChain.last_state_id")
    
    
    updated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True