from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Boolean, Date, Text, Table
from sqlalchemy.orm import relationship


problems_monitoring_files = Table('problems_monitoring_files', Base.metadata,
    Column('problems_monitoring_id', Integer(), ForeignKey("problems_monitoring.id")),
    Column('monitoring_files_id', Integer(), ForeignKey("monitoring_files.id"))
)



class ProblemsMonitoring(Base):
    __tablename__='problems_monitoring'
    id=Column(Integer, primary_key=True)
    problems_case_id = Column(Integer, ForeignKey('problems_case.id'), nullable = True, index=True)
    problems_monitoring_status_id = Column(Integer, ForeignKey('monitoring_status.id'), nullable = True)
    problems_monitoring_result_id = Column(Integer, ForeignKey('target_monitoring_result.id'), nullable = True)
    problems_monitoring_result_reason_id = Column(Integer, ForeignKey('result_reason.id'), nullable = True)
    problems_monitoring_result_reason_comment = Column(Text, nullable = True)
    project_status_id = Column(Integer, ForeignKey("financial_analysis_status.id"), nullable = True)
    amount=Column(String(20))
    main_responsible_due_date = Column(DateTime, nullable=True)
    second_responsible_due_date = Column(DateTime, nullable=True)
    deadline = Column(Date, nullable=True)
    created_at = Column(Date, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    problems_expiration = relationship('ProblemsMonitoringExpiration', backref='porblem_monitoring')
    files = relationship('MonitoringFiles', secondary=problems_monitoring_files, back_populates='problems_monitoring', overlaps="problems")
    
    class Config:
        orm_mode=True