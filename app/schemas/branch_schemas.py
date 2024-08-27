from pydantic import BaseModel
from typing import Optional


class Branch_request_schema(BaseModel):
    
    branch_name:str
    branch_number:int
        
    class Config:
        orm_mode=True