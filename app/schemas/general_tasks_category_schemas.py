from pydantic import BaseModel
from typing import List, Optional


class General_tasks_category_request_schema(BaseModel):
    name: str

        
    class Config:
        orm_mode=True
