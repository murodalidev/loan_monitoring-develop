from pydantic import BaseModel
from typing import List, Optional
import json


class ProblemsCaseSend(BaseModel):
    loan_portfolio_id:Optional[int]
    from_user:Optional[int]
    class Config:
        orm_mode=True
        
        
class SendToJuridicAfterTarget(BaseModel):
    general_task_id:Optional[int]
    case_id:Optional[int]
    intended_overdue_type_id:Optional[int]
    loan_portfolio_id:Optional[int]
    from_user:Optional[int]
    comment:Optional[str]

class SendToProblemAfterTarget(BaseModel):
    general_task_id:Optional[int]
    case_id:Optional[int]
    intended_overdue_type_id:Optional[int]
    amount:Optional[str]
    loan_portfolio_id:Optional[int]
    local_code_id:Optional[int]
    from_user:Optional[int]
    comment:Optional[str]

        
class JuridicalCaseAppoint(BaseModel):
    juridical_case_id:Optional[int]
    general_task_id:Optional[int]
    from_user:Optional[int]
    to_user:Optional[int]
    comment:Optional[str]
    
    class Config:
        orm_mode=True
   
   



class JudicialSendResults(BaseModel):
    problems_case_id:Optional[int]
    judicial_type_id:Optional[int]
    judicial_authority_type_id:Optional[int]
    region_id:Optional[int]
    judicial_authority_id:Optional[int]
    
    receipt_date:Optional[str] 
    decision_date_on_admission:Optional[str] 
    decision_date_to_set: Optional[str] 
    decision_date_in_favor_of_bank: Optional[str] 
    date_to_set:Optional[str]
    
    register_num: Optional[str] 
    decision_on_admission_num: Optional[str] 
    decision_to_set_num: Optional[str] 
    decision_in_favor_of_bank_num: Optional[str]
    
    claim_amount: Optional[str]
    from_user:Optional[int]
    to_user:Optional[int]
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




class AcceptOrReworkJudicialData(BaseModel):
    problems_case_id:Optional[int]
    judicial_data_id:Optional[int]
    wrong_files:Optional[List[int]]
    from_user:Optional[int]
    to_user:Optional[int]
    comment:Optional[str]
    result_type:bool
    class Config:
        orm_mode=True



class JudicialAuthorityCrud(BaseModel):
    judicial_authority_name:Optional[str]
    region_id:Optional[int]
    type_id:Optional[int]
    code:Optional[str]
    class Config:
        orm_mode=True






class JuridicalCaseAppointTaskSchema(BaseModel):
    juridical_case_id:Optional[int]
    task_manager_id:Optional[int]
    general_task_id:Optional[int]
    deadline:Optional[str]
    from_user:Optional[int]
    to_user:Optional[int]
    comment:Optional[str] 
    
    class Config:
        orm_mode=True
        
class JuridicalCaseAppointTask(BaseModel):
    juridical_case_id:Optional[int]
    task_manager_id:Optional[int]
    general_task_id:Optional[int]
    task_status:Optional[int]
    from_user:Optional[int]
    to_user:Optional[int]
    comment:Optional[str]
    deadline:Optional[str]
    
    
    
    
class JuridicalCaseSendToCheck(BaseModel):
    juridical_case_id:Optional[int]
    task_manager_id:Optional[int]
    intended_overdue_id:Optional[int]
    general_task_id:Optional[int]
    overdue_result:Optional[int]
    from_user:Optional[int]
    to_user:Optional[int]
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
        
        
class AppointSendLetter(BaseModel):
    problems_monitoring_id:Optional[int]
    task_manager_id:Optional[int]
    from_user:Optional[int]
    to_user:Optional[int]
    deadline:Optional[str]
    general_task_id:Optional[int]
    comment:Optional[str]
    
    class Config:
        orm_mode=True



class AcceptOrReworkTask(BaseModel):
    juridical_case_id:Optional[int]
    task_manager_id:Optional[int]
    intended_overdue_id:Optional[int]
    from_user:Optional[int]
    to_user:Optional[int]
    comment:Optional[str]
    result_type:Optional[bool]
    
    class Config:
        orm_mode=True
        
        

class AcceptSendLetter(BaseModel):
    task_manager_id:Optional[int]
    class Config:
        orm_mode=True



class SendLetter(BaseModel):
    branch_name:Optional[str]
    branch_phone:Optional[str]
    branch_address:Optional[str]
    client_name:Optional[str] 
    client_region:Optional[str]
    client_district:Optional[str]
    client_address:Optional[str] 
    overdue:Optional[str]
    overdue_days:Optional[str]
    overdue_perc:Optional[str]
    overdue_perc_days:Optional[str]
    overdue_total:Optional[str]
    total:Optional[str]
    branch_region:Optional[str]
    branch_manager:Optional[str]
    letter_id:Optional[str]
    letter_number:Optional[str]
    cur_date:Optional[str]
    problems_case_letter_id:Optional[int]
    task_manager_id:Optional[int]
    from_user:Optional[int]
    to_user:Optional[int]
    problems_monitoring_id:Optional[int]

    
    class Config:
        orm_mode=True



  

class UserSendToProblemsData():
    task_manager_id:int
    

class UpdateProblemsData():
    responsbile_id:int
    
    
    
    
class CloseProblemsCase(BaseModel):
    problems_letter_id:Optional[int]
    problems_monitoring_id:Optional[int]
    general_task_id:Optional[int]
    problems_case_id:Optional[int]
    loan_case_task_manager_id:Optional[int]
    from_user:Optional[int]
    to_user:Optional[int]
    loan_case_id:Optional[int]
    
    class Config:
        orm_mode=True
        
        
        
        
class ProblemsCaseSendJuridical(BaseModel):
    general_task_id:Optional[int]
    problems_case_id:Optional[int]
    intended_overdue_type_id:Optional[int]
    loan_portfolio_id:Optional[int]
    from_user:Optional[int]
    
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
        
        
        
        
        
class ReplyToNewLoan(BaseModel):
    general_task_id:Optional[int]
    juridical_case_id:Optional[int]
    loan_portfolio_id:Optional[int]
    from_user:Optional[int]
    to_user:Optional[int]
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
        
        
        
        
class AcceptOrRework(BaseModel):
    juridical_case_id:Optional[int]
    loan_portfolio_id:Optional[int]
    task_manager_id:Optional[int]
    from_user:Optional[int]
    to_user:Optional[int]
    general_task_id:Optional[int]
    comment:Optional[str]
    type:Optional[bool]
    
    class Config:
        orm_mode=True
        
        


class ReturnJuridical(BaseModel):
    juridical_case_id:Optional[int]
    loan_portfolio_id:Optional[int]
    from_user:Optional[int]
    general_task_id:Optional[int]
    
    class Config:
        orm_mode=True