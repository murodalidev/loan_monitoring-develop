from app.db.connect_db import Base
from sqlalchemy import Integer,Column, Column, Integer, ForeignKey, DateTime, Table, Boolean
from sqlalchemy.orm import relationship





class BusinessCase(Base):
    __tablename__='business_case'
    id=Column(Integer, primary_key=True)
    loan_portfolio_id = Column(Integer, ForeignKey('loan_portfolio.id'), nullable = True, index=True)
    main_responsible_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    main_responsible = relationship("Users", foreign_keys="BusinessCase.main_responsible_id")
    second_responsible_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    second_responsible = relationship("Users", foreign_keys="BusinessCase.second_responsible_id")
    business_monitoring_id = Column(Integer, ForeignKey('business_monitoring.id'), nullable = True)
    business_case_status_id = Column(Integer, ForeignKey('business_case_status.id'), nullable = True)
    checked_status = Column(Boolean, default=True, nullable = True)
    expired_status = Column(Boolean, default=False, nullable = True)
    from_type_id = Column(Integer, ForeignKey('from_type.id'), nullable = True)
    deadline_extension_status_id = Column(Integer, ForeignKey('deadline_extension.id'), nullable = True)
    task_manager_id = Column(Integer, ForeignKey('task_manager.id'), nullable = True, index=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True