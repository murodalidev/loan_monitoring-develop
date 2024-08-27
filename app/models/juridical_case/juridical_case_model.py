from app.db.connect_db import Base
from sqlalchemy import Integer,Column, Column, Integer, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship



juridical_case_files = Table('juridical_case_files', Base.metadata,
    Column('juridical_case_id', Integer(), ForeignKey("juridical_case.id")),
    Column('monitoring_files_id', Integer(), ForeignKey("monitoring_files.id"))
)





class JuridicalCase(Base):
    __tablename__='juridical_case'
    id=Column(Integer, primary_key=True)
    loan_portfolio_id = Column(Integer, ForeignKey('loan_portfolio.id'), nullable = True, index=True)
    main_responsible_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    main_responsible = relationship("Users", foreign_keys="JuridicalCase.main_responsible_id")
    second_responsible_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    second_responsible = relationship("Users", foreign_keys="JuridicalCase.second_responsible_id")
    from_user_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    from_user = relationship("Users", foreign_keys="JuridicalCase.from_user_id")
    intended_overdue_type_id = Column(Integer, ForeignKey('intended_overdue_type.id'), nullable = True)
    juridical_punishment_id = Column(Integer, ForeignKey('juridical_punishment.id'), nullable = True)
    juridical_case_status_id = Column(Integer, ForeignKey('juridical_case_status.id'), nullable = True)
    task_manager_id = Column(Integer, ForeignKey('task_manager.id'), nullable=True, index=True)
    juridical_intended = relationship('JuridicalIntendedOverdue', backref='juridical_case')
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True