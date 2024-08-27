from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Text, JSON, Table
from sqlalchemy.orm import relationship

loan_case_history_files = Table('loan_case_history_files', Base.metadata,
    Column('loan_case_history_id', Integer(), ForeignKey("loan_case_history.id")),
    Column('monitoring_files_id', Integer(), ForeignKey("monitoring_files.id"))
)




class LoanCaseHistory(Base):
    __tablename__='loan_case_history'
    id=Column(Integer, primary_key=True)
    loan_case_id = Column(Integer, ForeignKey('loan_case.id'), nullable = True, index = True)
    general_task_id = Column(Integer, ForeignKey('general_tasks.id'), nullable = True)
    type_id = Column(Integer, ForeignKey('case_history_type.id'), nullable = True)
    from_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    from_user = relationship("Users", foreign_keys="LoanCaseHistory.from_user_id")
    to_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    to_user = relationship("Users", foreign_keys="LoanCaseHistory.to_user_id")
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    comment = Column(Text, nullable=True)
    message = Column(Text, nullable=True)
    additional_data = Column(JSON, nullable=True)
    loan_case = relationship('LoanCase', backref='history')
    files = relationship('MonitoringFiles', secondary=loan_case_history_files, back_populates='loan_case_history', overlaps="casehistory")
    class Config:
        orm_mode=True