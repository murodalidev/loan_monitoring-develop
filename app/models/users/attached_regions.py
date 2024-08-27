from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey




class attached_regions(Base):
    __tablename__='attached_regions'
    id=Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    region_id = Column(Integer, ForeignKey('client_region.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    attached_type_id = Column(Integer, ForeignKey('attached_type.id'))
    
    class Config:
        orm_mode=True