from pydantic import BaseModel
from typing import List, Optional

class Departments_request_schema(BaseModel):
    department_name:Optional[str]
    region_id:Optional[int]
    
    class Config:
        orm_mode=True