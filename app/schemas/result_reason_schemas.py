from pydantic import BaseModel
from typing import List, Optional

class ResultReasonSchema(BaseModel):
    reason_name:str
    code:Optional[int]
        
    class Config:
        orm_mode=True