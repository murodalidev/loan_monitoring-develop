from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey




class permission(Base):
    __tablename__='permission'
    id=Column(Integer, primary_key=True)
    name = Column(String(70), nullable=True)
    route = Column(String(100), nullable=True)
    category_id = Column(Integer, ForeignKey('permission_category.id'))
    class Config:
        orm_mode=True