from fastapi import APIRouter, Depends
from app.db.connect_db import SessionManager
from typing import List, Optional
from app.services.kad_case import kad_case_crud, kad_balance_turnover_crud
from ....services.loan_monitoring.loan_case import loan_case_crud
from ....services.loan_monitoring.loan_porfolio import loan_portfolio_auto_distribution
from ....schemas.loan_portfolio_schemas import UserAcceptLoan, UserAcceptLoanList
from ....services.websocket.create_websocket import manager
import json
from app.middleware.auth_file import AuthHandler


auth_handler = AuthHandler()
router = APIRouter(
    prefix = "/kad-case", tags=["KAD Case"]
)


@router.get('/v1/get/all')
def kad_case(size:int, page:int, region_id:int=None, local_code_id:int=None, loan_id:int=None, client_name:str=None, product_type:int=None, 
             state_chain:int=None, client_type:str=None, currency_id:int=None, client_code:int=None, current_state:int=None, second_responsible:int=None,
               user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = kad_case_crud.get_all_kad_case(size, page, region_id, local_code_id, loan_id, client_name,
                                                    product_type, state_chain, second_responsible, client_type, currency_id, client_code, current_state, user.id,
                                                    user.department, db_session)
    return response




@router.get('/v1/get/turnover')
def business_case(size:int, page:int, region_id:int=None, local_code_id:int=None, loan_id:int=None, state_chain:int=None, client_name:str=None,
                  product_type:int=None, currency_id:int=None, client_type:str=None, main_responsible:int=None, second_responsible:int=None,
                  user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = kad_balance_turnover_crud.get_kad_all_turnover(size, page, user, region_id,local_code_id,client_name, currency_id, loan_id, state_chain, product_type, main_responsible, second_responsible, client_type, db_session)
    return response


@router.get('/v1/get/main-page-data')
def main_page_data(user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = kad_case_crud.get_kad_data_for_main_page(user.id, db_session)
    return response