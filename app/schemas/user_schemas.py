from pydantic import BaseModel
from typing import List, Optional



class UserCrud(BaseModel):
    username:Optional[str]
    full_name:Optional[str]
    region_id:Optional[int]
    local_code:Optional[int]
    department:Optional[int]
    position:Optional[int]
    head:Optional[int]
    status:Optional[int]
    password:Optional[str]
    pinfl:Optional[str]


    
    class Config:
        orm_mode=True



class UserLogin(BaseModel):
    username:str
    password:str

    class Config:
        orm_mode=True
        




class BranchesToUserAppendList(BaseModel):
    mfo_id:int

class BranchesToUserRemoveList(BaseModel):
    mfo_id:int


class BranchesToUser(BaseModel):
    user_id:int
    department_id:int
    attach_type:int
    mfo_list:Optional[List[int]]
    
        
    class Config:
        orm_mode=True
        
        
        
class LocalsToUser(BaseModel):
    user_id:int
    department_id:int
    attach_type:int
    local_code_list:Optional[List[int]]
    
        
    class Config:
        orm_mode=True
        
        


class RegionsToUser(BaseModel):
    user_id:int
    department_id:int
    attach_type:int
    region_list:Optional[List[int]]
    
        
    class Config:
        orm_mode=True





class Holiday(BaseModel):
    holiday:str
    
        
    class Config:
        orm_mode=True