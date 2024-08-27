from app.db.connect_db import Base
from sqlalchemy import String, Integer, Column, Integer, ForeignKey, DateTime, Table, Boolean, Text
from sqlalchemy.orm import relationship

judicial_data_files = Table('judicial_data_files', Base.metadata,
    Column('judicial_data_id', Integer(), ForeignKey("judicial_data.id")),
    Column('monitoring_files_id', Integer(), ForeignKey("monitoring_files.id"))
)




class JudicialData(Base):
    __tablename__='judicial_data'
    id=Column(Integer, primary_key=True)
    problems_case_id = Column(Integer, ForeignKey('problems_case.id'), nullable = True, index=True)
    type_id = Column(Integer, ForeignKey('judicial_type.id'), nullable = True)
    region_id = Column(Integer, ForeignKey('client_region.id'), nullable = True)
    authority_id = Column(Integer, ForeignKey('judicial_authority.id'), nullable = True)
    
    receipt_date = Column(DateTime, nullable = True)
    decision_date_on_admission = Column(DateTime, nullable = True)
    decision_date_to_set = Column(DateTime, nullable = True)
    decision_date_in_favor_of_bank = Column(DateTime, nullable = True)
    date_to_set = Column(DateTime, nullable = True)
    
    register_num = Column(String(30), nullable = True)
    decision_on_admission_num = Column(String(30), nullable = True)
    decision_to_set_num = Column(String(30), nullable = True)
    decision_in_favor_of_bank_num = Column(String(30), nullable = True)
    
    claim_amount = Column(String(30), nullable = True)
    judicial_status_id = Column(Integer, ForeignKey('problems_assets_status.id'), nullable = True)
    files = relationship('MonitoringFiles', secondary=judicial_data_files, back_populates='judicial_data', overlaps="judicial")
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True