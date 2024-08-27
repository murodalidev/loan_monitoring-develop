from app.db.connect_db import Base
from sqlalchemy import String,Integer,Column, Column, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship


class UserTgBotAuth(Base):
    __tablename__='user_tg_bot_auth'
    id=Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user_tg_bot_id = Column(Integer, nullable=True)
    tg_bot_token = Column(String(8), nullable=True)
    current_page = Column(Integer, nullable = True)
    user = relationship('Users', backref='auth')
    class Config:
        orm_mode=True
        
