from app.db.connect_db import Base
from sqlalchemy import Integer,Column, Column, Integer, ForeignKey, DateTime, Table, Boolean
from sqlalchemy.orm import relationship





class BusinessMonitoring(Base):
    __tablename__='business_monitoring'
    id=Column(Integer, primary_key=True)
    task_manager_id = Column(Integer, ForeignKey('task_manager.id'), nullable = True, index=True)
    business_monitoring_status_id = Column(Integer, ForeignKey('business_monitoring_status.id'), nullable = True)
    business_monitoring_result_id = Column(Integer, ForeignKey('business_monitoring_result.id'), nullable = True)
    deadline = Column(DateTime, nullable = True)
    main_responsible_due_date = Column(DateTime, nullable = True)
    second_responsible_due_date = Column(DateTime, nullable = True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True