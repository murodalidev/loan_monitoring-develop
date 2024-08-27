from app.db.connect_db import Base
from sqlalchemy import Integer,Column, Column, Integer, ForeignKey

class FilesTypes(Base):
    __tablename__='files_types'
    id=Column(Integer, primary_key=True)
    general_tasks_id = Column(Integer, ForeignKey('general_tasks.id'), nullable = True, index=True)
    f_types_id = Column(Integer, ForeignKey('f_types.id'), nullable = True, index=True)
    class Config:
        orm_mode=True