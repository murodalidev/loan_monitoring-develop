from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship

tasks_files = Table('tasks_files', Base.metadata,
    Column('task_manager_id', Integer(), ForeignKey("task_manager.id")),
    Column('monitoring_files_id', Integer(), ForeignKey("monitoring_files.id"))
)




class TaskManager(Base):
    __tablename__='task_manager'
    id=Column(Integer, primary_key=True)
    general_task_id = Column(Integer, ForeignKey('general_tasks.id'), nullable = True)
    task_status_id = Column(Integer, ForeignKey('task_status.id'), nullable = True)
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    loan_case = relationship('LoanCase', backref='task')
    business_case = relationship('BusinessCase', backref='task')
    target_monitoring = relationship('TargetMonitoring',  backref='task')
    hybrid_letters = relationship('HybridLetters',  backref='task')
    scheduled_monitoring = relationship('ScheduledMonitoring',  backref='task')
    unscheduled_monitoring = relationship('UnscheduledMonitoring',  backref='task')
    problems_case = relationship('ProblemsCase',  backref='task')
    juridic_case = relationship('JuridicalCase',  backref='task')
    intended_overdue = relationship('JuridicalIntendedOverdue',  backref='task')
    files = relationship('MonitoringFiles', secondary=tasks_files, back_populates='task_manager', overlaps="taskmanager")
    class Config:
        orm_mode=True