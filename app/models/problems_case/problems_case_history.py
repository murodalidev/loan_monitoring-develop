from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Text, JSON, Table
from sqlalchemy.orm import relationship

problems_case_history_files = Table('problems_case_history_files', Base.metadata,
    Column('problems_case_history_id', Integer(), ForeignKey("problems_case_history.id")),
    Column('monitoring_files_id', Integer(), ForeignKey("monitoring_files.id"))
)




class ProblemsCaseHistory(Base):
    __tablename__='problems_case_history'
    id=Column(Integer, primary_key=True)
    problems_case_id = Column(Integer, ForeignKey('problems_case.id'), nullable = True)
    general_task_id = Column(Integer, ForeignKey('general_tasks.id'), nullable = True)
    type_id = Column(Integer, ForeignKey('case_history_type.id'), nullable = True)
    from_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    from_user = relationship("Users", foreign_keys="ProblemsCaseHistory.from_user_id")
    to_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    to_user = relationship("Users", foreign_keys="ProblemsCaseHistory.to_user_id")
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    comment = Column(Text, nullable=True)
    message = Column(Text, nullable=True)
    additional_data = Column(JSON, nullable=True)
    problems_case = relationship('ProblemsCase', backref='history')
    files = relationship('MonitoringFiles', secondary=problems_case_history_files, back_populates='problems_case_history', overlaps="problemhistory")
    class Config:
        orm_mode=True