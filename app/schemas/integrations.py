from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import json
class Integration_log(BaseModel):
    loan_portfolio_id: Optional[int]
    loan_id: Optional[int]
    class Config:
        orm_mode=True

class SSP_integrations(BaseModel):
    loan_portfolio_id: int
    organizationId: int
    claimApplicationTypeId: int
    claimThemeId: int
    claimResponsibleTypeId: int
    details: Optional[str]
    penalty: Optional[float]
    otherDebtRepayment: Optional[float]
    currencyId: int
    phoneNumber: str
    PrevApplicationId: Optional[int]
    mainDebt: Optional[float]
    calculedPenalty: Optional[float]
    penalty: Optional[float]
    percent: Optional[float]
    currentPrincipalInterest: Optional[float]
    currentInterestRate: Optional[float]
    otherDebtRepayment: Optional[float]
    innOrPinfl: str
    fullName: str
    address: str
    
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


class Soliq_eauksion_orders(Integration_log):
    page: int
    per_page: int
    inn: str
    type: Optional[int]
    class Config:
        orm_mode=True


class Soliq_eauksion_orders_repotr(BaseModel):
    report_type:Optional[int]
    report_by:Optional[int]
    request: Soliq_eauksion_orders
    class Config:
        orm_mode=True


class Soliq_eauksion_order(Integration_log):
    order: int
    class Config:
        orm_mode=True


class Adliya_lifting_ban_imposed_by_bank(Integration_log):
    reg_num: str
    doc_type: str
    doc_num: str
    doc_date: int
    org_type: str
    org_name: str
    org_post: int
    org_fio: str
    base_document: str
    company_inn: str
    mfo: Optional[str]
    company_name: str
    representative_inn: Optional[str]
    representative_fio: str
    class Config:
        orm_mode=True


class Adliya_lifting_ban_imposed_by_notary(Integration_log):
    reg_num: str
    doc_type: str
    doc_num: str
    doc_date: str
    org_type: str
    org_name: str
    org_post: int
    org_fio: str
    base_document: str
    company_inn: str
    mfo: Optional[str]
    company_name: Optional[str]
    representative_inn: Optional[str]
    representative_fio: Optional[str]
    class Config:
        orm_mode=True


class MIB_debtors_info(Integration_log):
    sender_pinfl: str
    purpose: str
    type : Optional[int]
    consent: str
    pin_or_inn: str
    work_number: Optional[str]
    class Config:
        orm_mode=True


class Garov_notary_ban_list(Integration_log):
    member_type: str
    inn: Optional[str]
    pin: Optional[str]
    pass_serial: Optional[str]
    pass_num: Optional[str]
    subject_type: int
    cadastre_num: Optional[str]
    state_num: Optional[str]
    engine_num: Optional[str]
    body_num: Optional[str]
    chassis_num: Optional[str]
    vehicle_id: Optional[int]
    class Config:
        orm_mode=True


class Garov_notary_ban(Integration_log):
    code: str
    doc_num: str
    doc_date: date
    ban_edate: date
    #debtor: {
    subject_type: str
    country: str
    pass_type: str
    issue_org: str
    issue_date: date
    #}
    #object: {
    object_type: int
    cadaster_num: Optional[str]
    district: Optional[str]
    street: Optional[str]
    home: Optional[str]
    flat: Optional[str]
    block: Optional[str]
    obj_name: Optional[str]
    state_num: Optional[str]
    engine_num: Optional[str]
    body_num: Optional[str]
    chassis_num: Optional[str]
    mark: Optional[str]
    year_create: Optional[int]
    color: Optional[str]
    tech_serial: Optional[str]
    tech_num: Optional[str]
    tech_date: Optional[str]
    tech_issue: Optional[str]
    vehicle_id: Optional[int]
    #}
    class Config:
        orm_mode=True


class Garov_notary_ban_cancel(Integration_log):
    code: str
    ban_num: str
    doc_type: int
    doc_num: str
    doc_date: date
    class Config:
        orm_mode=True