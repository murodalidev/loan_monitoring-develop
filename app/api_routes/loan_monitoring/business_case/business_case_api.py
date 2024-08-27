from fastapi import APIRouter, Depends
from app.db.connect_db import SessionManager
from typing import List, Optional
from app.services.business_case import business_case_crud, business_balance_turnover_crud
from ....services.loan_monitoring.loan_case import loan_case_crud
from ....services.loan_monitoring.loan_porfolio import loan_portfolio_auto_distribution
from ....schemas.loan_portfolio_schemas import UserAcceptLoan, UserAcceptLoanList
from ....services.websocket.create_websocket import manager
import json
from app.middleware.auth_file import AuthHandler


auth_handler = AuthHandler()
router = APIRouter(
    prefix = "/business-case", tags=["Business Case"]
)


@router.get('/v1/get/all')
def business_case(size:int, page:int, region_id:int=None, local_code_id:int=None, loan_id:int=None, client_name:str=None, 
               is_target:int=None, product_type:int=None, client_type:str=None, client_code:int=None, second_responsible:int=None,
               
               user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = business_case_crud.get_all_business_case(size, page, region_id, local_code_id, loan_id, client_name, is_target,
                                                    product_type, client_type, second_responsible, client_code,  user.id, db_session)
    return response




@router.get('/v1/get/turnover')
def business_case(size:int, page:int, region_id:int=None, local_code_id:int=None, loan_id:int=None, client_name:str=None,
                  product_type:int=None, client_type:str=None, main_responsible:int=None, second_responsible:int=None,
                  user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = business_balance_turnover_crud.get_business_all_turnover(size, page, user, region_id,local_code_id,client_name, loan_id, product_type, client_type,
                                                                            main_responsible, second_responsible, db_session)
    return response


@router.get('/v1/get/main-page-data')
def main_page_data():
    with SessionManager() as db_session:
        response = business_case_crud.get_business_data_for_main_page(db_session)
    return response