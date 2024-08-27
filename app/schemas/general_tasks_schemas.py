from pydantic import BaseModel
from typing import List, Optional


class General_tasks_request_schema(BaseModel):
    name: Optional[str]
    category_id: Optional[int]
    level: Optional[int]
        
    class Config:
        orm_mode=True

class General_tasks_request_schema_update(BaseModel):
    name: Optional[str]
    level: Optional[int]
        
    class Config:
        orm_mode=True    