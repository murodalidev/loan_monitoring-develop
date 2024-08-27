from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey




class attached_branches(Base):
    __tablename__='attached_branches'
    id=Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    local_code_id = Column(Integer, ForeignKey('local_code.id'))
    department_id = Column(Integer, ForeignKey('departments.id'))
    attached_type_id = Column(Integer, ForeignKey('attached_type.id'))
    
    class Config:
        orm_mode=True