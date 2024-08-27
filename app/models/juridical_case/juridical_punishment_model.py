from app.db.connect_db import Base
from sqlalchemy import Integer,Column, Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship



class JuridicalPunishment(Base):
    __tablename__='juridical_punishment'
    id=Column(Integer, primary_key=True)
    main_responsible_id = Column(Integer, ForeignKey('users.id'), nullable = True, index=True)
    juridical_punishment_status_id = Column(Integer, ForeignKey('juridical_punishment_status.id'), nullable = True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    class Config:
        orm_mode=True