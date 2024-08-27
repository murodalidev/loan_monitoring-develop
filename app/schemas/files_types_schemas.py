from pydantic import BaseModel
from typing import List, Optional
import json




class FileTypesToGeneralTasks(BaseModel):
    general_task_id:int
    type_list:Optional[List[int]]
    
        
    class Config:
        orm_mode=True