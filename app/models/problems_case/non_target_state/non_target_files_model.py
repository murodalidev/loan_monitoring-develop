from app.db.connect_db import Base
from sqlalchemy import String, Integer, Column, Integer, ForeignKey, DateTime, Table, Boolean
from sqlalchemy.orm import relationship



class NonTargetStateFiles(Base):
    __tablename__='non_target_state_files'
    id = Column(Integer, primary_key=True)
    non_target_state_id = Column(Integer, ForeignKey('non_target_state.id'), nullable = True, index=True)
    file_url = Column(String(100))
    created_at = Column(DateTime, nullable=True)
    non_target_state = relationship('NonTargetState', backref='files')