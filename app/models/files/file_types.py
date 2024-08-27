from app.db.connect_db import Base
from sqlalchemy import Integer,Column, Column, Integer, ForeignKey, DateTime, String, Boolean
from sqlalchemy.orm import relationship

class FTypes(Base):
    __tablename__='f_types'
    id=Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True)
    code = Column(String(30), nullable = True)
    is_required = Column(Boolean, nullable = True)
    is_multiple = Column(Boolean, default=False)
    files = relationship('MonitoringFiles', backref='type')
    files_types = relationship('FilesTypes', backref='type')
    class Config:
        orm_mode=True