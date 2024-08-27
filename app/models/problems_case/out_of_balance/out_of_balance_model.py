from app.db.connect_db import Base
from sqlalchemy import String, Integer, Column, Integer, ForeignKey, DateTime, Table, Boolean
from sqlalchemy.orm import relationship

out_of_balance_files = Table('out_of_balance_files', Base.metadata,
    Column('out_of_balance_id', Integer(), ForeignKey("out_of_balance.id")),
    Column('monitoring_files_id', Integer(), ForeignKey("monitoring_files.id"))
)



class OutOfBalance(Base):
    __tablename__='out_of_balance'
    id=Column(Integer, primary_key=True)
    problems_case_id = Column(Integer, ForeignKey('problems_case.id'), nullable = True, index=True)
    main_responsible_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    main_responsible = relationship("Users", foreign_keys="OutOfBalance.main_responsible_id")
    second_responsible_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    second_responsible = relationship("Users", foreign_keys="OutOfBalance.second_responsible_id")
    third_responsible_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    third_responsible = relationship("Users", foreign_keys="OutOfBalance.third_responsible_id")
    turn = Column(Integer, nullable = True)
    out_of_balance_status_id = Column(Integer, ForeignKey('problems_assets_status.id'), nullable = True)
    
    files = relationship('MonitoringFiles', secondary=out_of_balance_files , back_populates='out_of_balance', overlaps="assets")
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True