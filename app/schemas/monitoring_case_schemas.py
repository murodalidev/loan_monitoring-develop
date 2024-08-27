from pydantic import BaseModel
from typing import List, Optional
import json
class MonitoringCaseAppoint(BaseModel):
    second_responsible_id:Optional[int]
    loan_case_id:Optional[int]
    task_manager_id:Optional[int]
    general_task_id:Optional[int]
    
    class Config:
        orm_mode=True
 

class AcceptedLoanCaseList(BaseModel):
    loan_case_id:int
class LoanCaseChangeResponsible(BaseModel):
    accept:Optional[List[int]]
    second_responsible_id:int
    class Config:
        orm_mode=True
 
        
        
class TargetMonitoringAppoint(BaseModel):
    monitoring_case_id:Optional[int]
    general_task_id:Optional[int]
    main_responsible_id:Optional[int]
    second_responsible_id:Optional[int]
    comment:str
    deadline:Optional[str]
    
    class Config:
        orm_mode=True
        
        
class ScheduledMonitoringAppoint(BaseModel):
    loan_case_id:Optional[int]
    monitoring_case_id:Optional[int]
    general_task_id:Optional[int]
    main_responsible_id:Optional[int]
    second_responsible_id:Optional[int]
    frequency_period_id:Optional[int]
    loan_issue_date:Optional[str]
    comment:str
    
    class Config:
        orm_mode=True


class UnscheduledMonitoringAppoint(BaseModel):
    loan_case_id:Optional[int]
    monitoring_case_id:Optional[int]
    main_responsible_id:Optional[int]
    second_responsible_id:Optional[int]
    deadline:Optional[str]
    comment:str
    
    class Config:
        orm_mode=True


 

class ScheduledMonitoringReport(BaseModel):
    scheduled_monitoring_id:Optional[int]
    task_manager_id:Optional[int]
    frequency_period_id:Optional[int]
    start_date:Optional[str]
    end_date:Optional[str]
    
    class Config:
        orm_mode=True


        
class AcceptOrReworkTargetMonitoring(BaseModel):
    loan_case_id:Optional[int]
    target_monitoring_id:Optional[int]
    task_manager_id:Optional[int]
    general_task_id:Optional[int]
    from_user:Optional[int]
    to_user:Optional[int]
    wrong_files:Optional[List[int]]
    comment:Optional[str]
    result_type:bool
    class Config:
        orm_mode=True


class AcceptOrReworkScheduledMonitoring(BaseModel):
    loan_case_id:Optional[int]
    scheduled_monitoring_id:Optional[int]
    task_manager_id:Optional[int]
    from_user:Optional[int]
    to_user:Optional[int]
    wrong_files:Optional[List[int]]
    comment:Optional[str]
    result_type:bool
    class Config:
        orm_mode=True
        
   
class AcceptOrReworkUnscheduledMonitoring(BaseModel):
    loan_case_id:Optional[int]
    unscheduled_monitoring_id:Optional[int]
    task_manager_id:Optional[int]
    from_user:Optional[int]
    to_user:Optional[int]
    wrong_files:Optional[List[int]]
    comment:Optional[str]
    result_type:bool
    class Config:
        orm_mode=True
   
        
        
        
        
class TargetMonitoringCheck(BaseModel):
    amount:Optional[int]
    task_manager_id:Optional[int]
    loan_case_id:Optional[int]
    target_monitoring_id:Optional[int]
    target_monitoring_result:Optional[int]
    target_monitoring_result_reason:Optional[int]
    target_monitoring_result_reason_other:Optional[str]
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
        
        
        
        
        
class ScheduledMonitoringCheck(BaseModel):
    loan_case_id:Optional[int]
    scheduled_monitoring_id:Optional[int]
    scheduled_monitoring_result_id:Optional[int]
    scheduled_monitoring_result_reason:Optional[int]
    scheduled_monitoring_result_reason_other:Optional[str]
    amount:Optional[int]
    project_status_id:Optional[int]
    task_manager_id:Optional[int]
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
        


class UnscheduledMonitoringCheck(BaseModel):
    loan_case_id:Optional[int]
    unscheduled_monitoring_id:Optional[int]
    unscheduled_monitoring_result_id:Optional[int]
    unscheduled_monitoring_result_reason_id:Optional[int]
    unscheduled_monitoring_result_reason_other:Optional[str]
    project_status_id:Optional[int]
    amount:Optional[int]
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
        
   
        


class LoanCaseHistory(BaseModel):
    loan_case_id:Optional[int]
    general_task_id:Optional[int]
    class Config:
        orm_mode=True
        

class LoanCaseClose(BaseModel):
    loan_case_id:Optional[int]
    task_manager_id:Optional[int]
    general_task_id:Optional[int]
    class Config:
        orm_mode=True
        
class CreateFinAnalysis(BaseModel):
    loan_case_id:Optional[int]
    from_user:Optional[int]
    comment:Optional[str]
    monitoring_case_id: Optional[int] 
    income_plan: Optional[str]
    income_fact: Optional[str]
    profit_plan: Optional[str]
    profit_fact: Optional[str]
    expences_plan: Optional[str]
    expences_fact: Optional[str]
    net_profit_plan: Optional[str]
    net_profit_fact: Optional[str]
    new_workplaces_plan: Optional[str]
    new_workplaces_fact: Optional[str]
    financial_analysis_status_id: Optional[int]
    class Config:
        orm_mode=True
        
        
        
        
        
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
        
        


class TargetTemplate(BaseModel):
    loan_portfolio_id:Optional[int]
    
    
class ExcelReportPeriod(BaseModel):
    start_date:Optional[str]
    end_date:Optional[str]
    report_type:Optional[int]
    report_by:Optional[int]