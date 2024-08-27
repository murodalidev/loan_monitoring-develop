from app.db.connect_db import Base
from sqlalchemy import Integer,Column, Column, Integer, ForeignKey, DateTime, String, Boolean, Table
from sqlalchemy.orm import relationship
from app.models.problems_case.judicial_process.judicial_process_data_model import judicial_data_files
from app.models.monitoring_task_manager.task_manager_model import tasks_files
from app.models.loan_case.loan_case_history_model import loan_case_history_files
from app.models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_model import unscheduled_monitoring_files
from app.models.monitoring_case.scheduled_monitoring_model import scheduled_monitoring_files
from app.models.monitoring_case.target_monitoring_model import target_monitoring_files
from app.models.monitoring_case.extension_history_model import target_extension_files, scheduled_extension_files, unscheduled_extension_files
from app.models.problems_case.problems_case_history import problems_case_history_files
from app.models.problems_case.problems_case_model import problems_files
from app.models.problems_case.problems_monitoring_model import problems_monitoring_files
from app.models.problems_case.problems_assets.problems_assets_model import problems_assets_files
from app.models.problems_case.out_of_balance.out_of_balance_model import out_of_balance_files



class MonitoringFiles(Base):
    __tablename__='monitoring_files'
    id=Column(Integer, primary_key=True)
    file_url = Column(String(255), nullable=True)
    ftype = Column(Integer, ForeignKey('f_types.id'), nullable = True)
    is_correct = Column(Boolean, default=True)
    is_changed = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    task_manager = relationship('TaskManager', secondary=tasks_files, back_populates='files')
    loan_case_history = relationship('LoanCaseHistory', secondary=loan_case_history_files, back_populates='files')
    scheduled_monitoring = relationship('ScheduledMonitoring', secondary=scheduled_monitoring_files, back_populates='files')
    scheduled_extension = relationship('ScheduledDeadlineExtensionMonitoringHistory', secondary=scheduled_extension_files, back_populates='files')
    unscheduled_monitoring = relationship('UnscheduledMonitoring', secondary=unscheduled_monitoring_files, back_populates='files')
    unscheduled_extension = relationship('UnscheduledDeadlineExtensionMonitoringHistory', secondary=unscheduled_extension_files, back_populates='files')
    target_monitoring = relationship('TargetMonitoring', secondary=target_monitoring_files, back_populates='files')
    target_extension = relationship('TargetDeadlineExtensionMonitoringHistory', secondary=target_extension_files, back_populates='files')
    problems_case_history = relationship('ProblemsCaseHistory', secondary=problems_case_history_files, back_populates='files')
    problems_case = relationship('ProblemsCase', secondary=problems_files, back_populates='files')
    problems_monitoring = relationship('ProblemsMonitoring', secondary=problems_monitoring_files, back_populates='files')
    judicial_data = relationship('JudicialData', secondary=judicial_data_files, back_populates='files')
    problems_assets = relationship('ProblemsAssets', secondary=problems_assets_files, back_populates='files')
    out_of_balance = relationship('OutOfBalance', secondary=out_of_balance_files, back_populates='files')
    class Config:
        orm_mode=True