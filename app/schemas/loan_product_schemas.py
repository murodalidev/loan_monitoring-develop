from pydantic import BaseModel
from typing import List, Optional

class LoanProduct(BaseModel):
    loan_product_name:Optional[str]
    loan_product_type_id:Optional[int]
    is_target:Optional[int]
    
    class Config:
        orm_mode=True
        
        
        
        
class LocalCode(BaseModel):
    name:Optional[str]
    code:Optional[str]
    region_id:Optional[int]
    head:Optional[int]
    index:Optional[str]
    address:Optional[str]                                     
    inn:Optional[str]
    phone_number:Optional[str]
    manager:Optional[str]
    
    class Config:
        orm_mode=True