from pydantic import BaseModel
from typing import Optional, List
from .integrations import Integration_log

class Check_Family(Integration_log):
    
    base_pinfl:str
    list_check_pinfl:List[str]
        
    class Config:
        orm_mode=True
        
        
        
class Declarant(BaseModel):
    company_inn:Optional[str]
    mfo:Optional[str]
    company_name:Optional[str]
    representative_inn:Optional[str]
    representative_fio:Optional[str]    
      
    class Config:
        orm_mode=True


class Member(BaseModel):
    member_type:Optional[int]
    inn:Optional[str]
    member_pinfl:Optional[str]
    pass_serial:Optional[str]
    pass_num:Optional[str]    
    class Config:
        orm_mode=True
        
class Subject(BaseModel):
    subject_type:Optional[int]
    cadastre_num:Optional[str]
    state_num:Optional[str]
    engine_num:Optional[str]
    body_num:Optional[str]
    chassis_num:Optional[str]
    class Config:
        orm_mode=True

class Notarial_Ban(Integration_log):
    
    reg_num:str
    declarant:Declarant
    member:Member
    subject:Subject
        
    class Config:
        orm_mode=True
        
        

class Notarial_Ban_By_Subject(Integration_log):
    subject_type:int
    cadastre_num:Optional[str]
    state_num:Optional[str]
    engine_num:Optional[str]
    body_num:Optional[str]
    chassis_num:Optional[str]
    vehicle_id:Optional[int]
    class Config:
        orm_mode=True