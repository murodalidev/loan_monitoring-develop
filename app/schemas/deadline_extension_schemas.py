from pydantic import BaseModel
from typing import List, Optional
import json

class DeadlineExtension(BaseModel):
    loan_case_id:Optional[int]
    case_type_id:Optional[int]
    to_user_id:Optional[int]
    comment:Optional[str]
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    class Config:
        orm_mode=True
        
        


class AcceptOrDeclineExtension(BaseModel):
    loan_case_id:Optional[int]
    case_type_id:Optional[int]
    to_user:Optional[int]
    result:Optional[bool]
    date:Optional[str]
    comment:Optional[str]