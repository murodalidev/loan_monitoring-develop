from pydantic import BaseModel
from typing import List, Optional



class AcceptedLoanList(BaseModel):
    loan_portfolio_id:int

class UserAcceptLoan(BaseModel):
    accept:Optional[Optional[List[int]]]
        
    class Config:
        orm_mode=True



class AcceptedLoanListWithLoanProduct(BaseModel):
    loan_portfolio_id:int
    loan_product:str
class UserAcceptLoanList(BaseModel):
    accept:Optional[List[AcceptedLoanListWithLoanProduct]]
    second_responsible_id:int
    class Config:
        orm_mode=True
        
        
        
        
class UserAcceptedLoanData():
    task_manager_id:int
    
    
class CreateLoanCase():
    loan_portfolio_id:int
    main_responsible_id:int
    second_responsible_id:int
    