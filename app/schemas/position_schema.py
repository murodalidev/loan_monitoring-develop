from pydantic import BaseModel
from typing import List, Optional

class Position_request_schema(BaseModel):
    position_name:str
        
    class Config:
        orm_mode=True