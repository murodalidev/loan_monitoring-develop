from pydantic import BaseModel
from typing import List, Optional

 
 
 
        
class UpdateTaskManagerSetResponsible():
    task_manager_id:int
    general_task_id:int
    deadline:int
    task_status:int
    letter_num:int
    
class UpdateTaskManagerAccept():
    task_manager_id:int
    general_task_id:int
    task_status:int
    
class CreateTaskManagerSetTargetMonitoring():
    task_manager_id:int
    general_task_id:int
    from_user:Optional[int]
    to_user:Optional[int]
    comment:Optional[str]
    created_at:Optional[str]
    deadline:Optional[str]
    
    
    
class UpdateTaskManagerSendToCheck():
    task_manager_id:int
    task_status:Optional[int]
    from_user:Optional[int]
    to_user:Optional[int]
    comment:Optional[str]
    
class UpdateTaskManagerClose():
    task_manager_id:int
    general_task_id:int
    task_status:int
    
    
    
class GetaskManager():
    task_manager_id:int