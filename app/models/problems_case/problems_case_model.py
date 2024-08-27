from app.db.connect_db import Base
from sqlalchemy import String, Integer, Column, Integer, ForeignKey, DateTime, Table, Boolean
from sqlalchemy.orm import relationship

problems_files = Table('problems_files', Base.metadata,
    Column('problems_case_id', Integer(), ForeignKey("problems_case.id")),
    Column('monitoring_files_id', Integer(), ForeignKey("monitoring_files.id"))
)



class ProblemsCase(Base):
    __tablename__='problems_case'
    id=Column(Integer, primary_key=True)
    loan_portfolio_id = Column(Integer, ForeignKey('loan_portfolio.id'), nullable = True, index=True)
    main_responsible_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    main_responsible = relationship("Users", foreign_keys="ProblemsCase.main_responsible_id")
    second_responsible_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    second_responsible = relationship("Users", foreign_keys="ProblemsCase.second_responsible_id")
    problems_case_status_id = Column(Integer, ForeignKey('problems_case_status.id'), nullable = True)
    non_target_amount = Column(String(20), nullable = True)
    checked_status = Column(Boolean, default=True, nullable = True)
    expired_status = Column(Boolean, default=False, nullable = True)
    from_type_id = Column(Integer, ForeignKey('from_type.id'), nullable = True)
    deadline_extension_status_id = Column(Integer, ForeignKey('deadline_extension.id'), nullable = True)
    task_manager_id = Column(Integer, ForeignKey('task_manager.id'), nullable=True, index=True)
    files = relationship('MonitoringFiles', secondary=problems_files, back_populates='problems_case', overlaps="problems")
    problem_monitoring = relationship('ProblemsMonitoring', backref='problem_case')
    judicial_data = relationship('JudicialData', backref='problem_case')
    problems_assets = relationship('ProblemsAssets', backref='problem_case')
    non_target_state = relationship('NonTargetState', backref='problem_case')
    auction = relationship('ProblemsAuction', backref='problem_case')
    mib_ended = relationship('ProblemsMib', backref='problem_case')
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True