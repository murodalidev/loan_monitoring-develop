from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship


user_role = Table('user_role', Base.metadata,
    Column('user_id', Integer(), ForeignKey("users.id")),
    Column('role_id', Integer(), ForeignKey("roles.id"))
)



class Users(Base):
    __tablename__='users'
    id=Column(Integer, primary_key=True)
    full_name=Column(String(50))
    username = Column(String(30))
    password = Column(String(70))
    region_id = Column(Integer, ForeignKey('client_region.id'))
    local_code = Column(Integer, ForeignKey('local_code.id'))
    department = Column(Integer, ForeignKey('departments.id'))
    position = Column(Integer, ForeignKey('positions.id'))
    head = Column(Integer, ForeignKey('users.id'))
    status = Column(Integer, ForeignKey('user_status.id'))
    password_status = Column(Integer)
    token = Column(String(200), nullable=True)
    real_ip = Column(String(16), nullable=True)
    pinfl =  Column(String(14), nullable=True)
    attached = relationship('attached_branches', backref='user')
    heads = relationship('Users', backref='sub', remote_side=[id])
    roles = relationship('roles', secondary=user_role, back_populates='users', overlaps="user")
    class Config:
        orm_mode=True
        
