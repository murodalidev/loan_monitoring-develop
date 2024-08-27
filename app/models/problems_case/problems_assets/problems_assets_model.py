from app.db.connect_db import Base
from sqlalchemy import String, Integer, Column, Integer, ForeignKey, DateTime, Table, Boolean
from sqlalchemy.orm import relationship

problems_assets_files = Table('problems_assets_files', Base.metadata,
    Column('problems_assets_id', Integer(), ForeignKey("problems_assets.id")),
    Column('monitoring_files_id', Integer(), ForeignKey("monitoring_files.id"))
)



class ProblemsAssets(Base):
    __tablename__='problems_assets'
    id=Column(Integer, primary_key=True)
    problems_case_id = Column(Integer, ForeignKey('problems_case.id'), nullable = True, index=True)
    type_id = Column(Integer, ForeignKey('problems_assets_type.id'), nullable = True)
    main_responsible_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    main_responsible = relationship("Users", foreign_keys="ProblemsAssets.main_responsible_id")
    second_responsible_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    second_responsible = relationship("Users", foreign_keys="ProblemsAssets.second_responsible_id")
    third_responsible_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    third_responsible = relationship("Users", foreign_keys="ProblemsAssets.third_responsible_id")
    turn = Column(Integer, nullable = True)
    assets_status_id = Column(Integer, ForeignKey('problems_assets_status.id'), nullable = True)
    
    files = relationship('MonitoringFiles', secondary=problems_assets_files , back_populates='problems_assets', overlaps="assets")
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True