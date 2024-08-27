from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer,ForeignKey, Table
from sqlalchemy.orm import relationship
from app.models.users.users import user_role

role_permissions = Table('role_permission', Base.metadata, 
    Column('role_id', Integer(), ForeignKey("roles.id")),
    Column('permission_id', Integer(), ForeignKey("permission.id"))
    
)




class roles(Base):
    __tablename__='roles'
    id=Column(Integer, primary_key=True)
    name = Column(String(100))
    role_permission = relationship('permission', secondary=role_permissions, backref='permission')
    level = Column(Integer)
    users = relationship('Users', secondary=user_role, back_populates='roles')
    
    class Config:
        orm_mode=True