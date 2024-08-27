from pydantic import BaseModel
from typing import List, Optional

 
 
class Notification_request(BaseModel):
    id: int

    class Config:
        orm_mode = True
        
class CreateNotification():
    from_user_id:int
    to_user_id:int
    notification_type:int
    body:str
    url:str
    
    
class ReadNotification():
    user_id:int
    notification_id:int
    notifications:List[int]
    
class CreateLoanCase(BaseModel):
    loan_portfolio_id:int
    main_responsible_id:int
    
    class Config:
        orm_mode=True