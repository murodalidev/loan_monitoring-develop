from app.db.connect_db import Base
from sqlalchemy import Integer,Column, Column, Integer, ForeignKey, DateTime, Table, Boolean
from sqlalchemy.orm import relationship





class LoanCase(Base):
    __tablename__='loan_case'
    id=Column(Integer, primary_key=True)
    loan_portfolio_id = Column(Integer, ForeignKey('loan_portfolio.id'), nullable = True, index=True)
    main_responsible_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    main_responsible = relationship("Users", foreign_keys="LoanCase.main_responsible_id")
    second_responsible_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    second_responsible = relationship("Users", foreign_keys="LoanCase.second_responsible_id")
    monitoring_case_id = Column(Integer, ForeignKey('monitoring_case.id'), nullable = True)
    loan_case_status_id = Column(Integer, ForeignKey('loan_case_status.id'), nullable = True)
    expired_status = Column(Boolean, default=False, nullable = True)
    checked_status = Column(Boolean, default=False, nullable = True)
    target_deadline_extension_status_id = Column(Integer, ForeignKey('deadline_extension.id'), nullable = True)
    target_deadline_extension_status = relationship("DeadlineExtension", foreign_keys="LoanCase.target_deadline_extension_status_id")
    
    scheduled_deadline_extension_status_id = Column(Integer, ForeignKey('deadline_extension.id'), nullable = True)
    scheduled_deadline_extension_status = relationship("DeadlineExtension", foreign_keys="LoanCase.scheduled_deadline_extension_status_id")
    
    unscheduled_deadline_extension_status_id = Column(Integer, ForeignKey('deadline_extension.id'), nullable = True)
    unscheduled_deadline_extension_status = relationship("DeadlineExtension", foreign_keys="LoanCase.unscheduled_deadline_extension_status_id")
    
    task_manager_id = Column(Integer, ForeignKey('task_manager.id'), nullable = True, index=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True