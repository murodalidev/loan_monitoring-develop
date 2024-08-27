from app.db.connect_db import Base
from sqlalchemy import Column, Integer, String





class Integrations_service(Base):
    __tablename__='integrations_service'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    code = Column(Integer)