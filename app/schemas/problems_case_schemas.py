from pydantic import BaseModel
from typing import List, Optional
import json


class ProblemsCaseSend(BaseModel):
    loan_case_id:Optional[int]
    general_task_id:Optional[int]
    loan_portfolio_id:Optional[int]
    from_user:Optional[int]
    class Config:
        orm_mode=True
        
        
        
class ProblemsCaseAppoint(BaseModel):
    problems_case_id:Optional[int]
    general_task_id:Optional[int]
    from_user:Optional[int]
    to_user:Optional[int]
    comment:Optional[str]
    
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
        
class AcceptSendLetter(BaseModel):
    task_manager_id:Optional[int]
    class Config:
        orm_mode=True




class ProblemsMonitoringAppoint(BaseModel):
    problems_case_id:Optional[int]
    main_responsible_id:Optional[int]
    second_responsible_id:Optional[int]
    deadline:Optional[str]
    comment:str
    
    class Config:
        orm_mode=True



class ProblemsMonitoringSendResults(BaseModel):
    problems_case_id:Optional[int]
    problems_monitoring_id:Optional[int]
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




class AcceptOrReworkProblemsMonitoring(BaseModel):
    problems_case_id:Optional[int]
    problems_monitoring_id:Optional[int]
    from_user:Optional[int]
    to_user:Optional[int]
    wrong_files:Optional[List[int]]
    comment:Optional[str]
    result_type:bool
    class Config:
        orm_mode=True






class GenerateLetter(BaseModel):
    letter_receiver_type_id:Optional[int]
    local_name:Optional[str]
    client_name:Optional[str] 
    client_region:Optional[str]
    client_district:Optional[str]
    client_address:Optional[str] 
    issue_date:Optional[str]
    loan_id:Optional[int]
    loan_purpose:Optional[str]
    loan_period:Optional[str]
    percent:Optional[str]
    loan_amount:Optional[str]
    schedule_day:Optional[int]
    total_overdue:Optional[str]
    overdue_balance:Optional[str]
    balance_16377:Optional[str]
    total_balance:Optional[str]
    branch_region:Optional[str]
    borrower_type:Optional[str]
    kad_case_id:Optional[int]
    general_task_id:Optional[int]
    cur_date:Optional[str]
    comment:Optional[str]

    
    class Config:
        orm_mode=True


class SendLetter(BaseModel):
    #from_user:Optional[int]
    loan_portfolio_id:Optional[int]
    kad_case_id:Optional[int]
    general_task_id:Optional[int]
    comment:Optional[str]

    
    class Config:
        orm_mode=True

class AppendLetter(BaseModel):
    letter_receiver_type_id:int
    monitoring_case_id:int
    general_task_id:int
    comment:Optional[str]
    send_date: str
    post_id: str
    
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


  

class UserSendToProblemsData():
    task_manager_id:int
    

class UpdateProblemsData():
    responsbile_id:int
    
    
    
    
class CloseProblemsCase(BaseModel):
    #problems_letter_id:Optional[int]
    problems_monitoring_id:Optional[int]
    general_task_id:Optional[int]
    problems_case_id:Optional[int]
    from_user:Optional[int]
    
    class Config:
        orm_mode=True
        
        
        
        
class ProblemsCaseSendJuridical(BaseModel):
    general_task_id:Optional[int]
    case_id:Optional[int]
    intended_overdue_type_id:Optional[int]
    loan_portfolio_id:Optional[int]
    from_user:Optional[int]
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



class ProblemsAssetsSendResults(BaseModel):
    problems_case_id:Optional[int]
    from_user:Optional[int]
    asset_type_id:Optional[int]
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



class OutOfBalanceSendResults(BaseModel):
    problems_case_id:Optional[int]
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



class ProblemsAssetsLawyerSendResult(BaseModel):
    problems_case_id:Optional[int]
    problems_assets_id:Optional[int]
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




class OutOfBalanceLawyerSendResult(BaseModel):
    problems_case_id:Optional[int]
    out_of_balance_id:Optional[int]
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




class ProblemsAssetsAcceptOrRework(BaseModel):
    problems_case_id:Optional[int]
    problems_assets_id:Optional[int]
    from_user:Optional[int]
    result_type:Optional[int]
    to_user:Optional[int]
    comment:Optional[str]
    wrong_files:Optional[List[int]]



class OutOfBalanceAcceptOrRework(BaseModel):
    problems_case_id:Optional[int]
    out_of_balance_id:Optional[int]
    from_user:Optional[int]
    result_type:Optional[int]
    to_user:Optional[int]
    comment:Optional[str]
    wrong_files:Optional[List[int]]
        
        
        
class ReplyToNewLoan(BaseModel):
    general_task_id:Optional[int]
    case_id:Optional[int]
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
        
        
        
        


class SendLetterToNonTarget(BaseModel):
    client_name:Optional[str] 
    client_address:Optional[str]
    loan_id:Optional[int]
    branch_region:Optional[str]
    problems_case_id:Optional[int]
    loan_portfolio_id:Optional[int]

    
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
        
        
        
        
        
        
        
        
class SendNonTargetStateFiles(BaseModel):
    problems_case_id:Optional[int]
    non_target_type_id:Optional[int]
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
        
        


class SendAuctionFiles(BaseModel):
    problems_case_id:Optional[int]
    auction_type_id:Optional[int]
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
        
        



class SendMibFiles(BaseModel):
    problems_case_id:Optional[int]
    mib_type_id:Optional[int]
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
        
        
        

class AcceptOrReworkMibData(BaseModel):
    problems_case_id:Optional[int]
    mib_ended_id:Optional[int]
    wrong_files:Optional[List[int]]
    from_user:Optional[int]
    to_user:Optional[int]
    comment:Optional[str]
    result_type:bool
    class Config:
        orm_mode=True
        
        



class AcceptOrReworkAuction(BaseModel):
    problems_case_id:Optional[int]
    auction_id:Optional[int]
    wrong_files:Optional[List[int]]
    from_user:Optional[int]
    to_user:Optional[int]
    comment:Optional[str]
    result_type:bool
    class Config:
        orm_mode=True