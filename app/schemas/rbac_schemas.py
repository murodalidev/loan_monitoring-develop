from pydantic import BaseModel
from typing import Optional, List


class NameForPathList(BaseModel):
    name:str
    permission_id:int


class Name_for_path(BaseModel):
    
    names:List[NameForPathList]
        
    class Config:
        orm_mode=True
        
        
class PermissionToUserAppendList(BaseModel):
    permission_id:int

class PermissionToUserRemoveList(BaseModel):
    permission_id:int


class PermissionToUser(BaseModel):
    role_id:int
    append:Optional[List[PermissionToUserAppendList]]
    remove:Optional[List[PermissionToUserRemoveList]]
        
    class Config:
        orm_mode=True
        
        
        
class Role(BaseModel):
    name: Optional[str]
    level: Optional[int]

    class Config:
        orm_mode=True
        
        
        
class User_role(BaseModel):
    role: List[int]
    class Config:
        orm_mode=True

