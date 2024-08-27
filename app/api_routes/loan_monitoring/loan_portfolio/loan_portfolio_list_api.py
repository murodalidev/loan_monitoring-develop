from fastapi import APIRouter, Depends
from app.db.connect_db import SessionManager
from ....common import common_handler
from app.services.loan_monitoring.loan_porfolio import loan_portfolio_list
from ....services.loan_monitoring.loan_case import loan_case_crud, loan_case_get
from ....services.loan_monitoring.loan_porfolio import loan_portfolio_auto_distribution
from ....schemas.loan_portfolio_schemas import UserAcceptLoan, UserAcceptLoanList
from ....services.websocket.create_websocket import manager
import json
from app.middleware.auth_file import AuthHandler


auth_handler = AuthHandler()
router = APIRouter(
    prefix = "/portfolio-list", tags=["Loan Porfolio List"]
)

@router.get('/v1/get-by-param')
def portrfolio(page:int, size:int, region_id:int=None, loan_id:int=None,client_name:str=None, client_code:int=None, is_target:int=None, client_type:str=None, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = common_handler.handle_error(loan_portfolio_list.get_loan_porfolio,page,size, region_id, user.local_code, loan_id, client_name,
                                               client_code, is_target, client_type,  user.department, db_session)
    return response

@router.get('/v1/get-details')
def portrfolio(loan_portfolio_id:int):
    with SessionManager() as db_session:
        response = common_handler.handle_error(loan_portfolio_list.get_loan_portfolio_details, loan_portfolio_id, db_session)
    return response



@router.post('/v1/accept-task')
def portrfolio(request: UserAcceptLoan, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = common_handler.handle_error(loan_portfolio_list.user_accept_loan, request, user.id, user.department, db_session)
        # message = {'notification_message':'accept task', 'type':'loan'}
        # await manager.local_broadcast(response,json.dumps(message))
    return response


@router.post('/v1/accept-list-task')
def portrfolio(request: UserAcceptLoanList, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = common_handler.handle_error(loan_portfolio_list.user_accept_loan_list, request, user.id, user.department, db_session)
        # message = {'notification_message':'accept task', 'type':'loan'}
        # await manager.local_broadcast(response,json.dumps(message))
    return response



# @router.get('/v1/case/get/all')
# def portrfolio(size:int, page:int, region_id:int=None, local_code_id:int=None, loan_id:int=None, client_name:str=None, 
#                is_target:int=None, product_type:int=None, client_type:str=None, task_status_id:int=None, client_code:int=None, expired:bool=None,
#                start_period:str=None, end_period:str=None,
#                user=Depends(auth_handler.auth_wrapper)):
#     with SessionManager() as db_session:
#         db_session.add(user)
#         response = common_handler.handle_error(loan_case_crud.get_all_loan_case, size, page, region_id, local_code_id, loan_id, client_name, is_target,
#                                                     product_type, client_type, task_status_id, client_code, expired, start_period, end_period, user.id,
#                                                     user.department, db_session)
#     return response


@router.get('/v2/case/get/all')
def portrfolio(size:int, page:int, region_id:int=None, local_code_id:int=None, loan_id:int=None, client_name:str=None, 
               is_target:int=None, product_type:int=None, client_type:str=None, task_status_id:int=None,lending_type:str=None, client_code:int=None, monitoring_stage:int=None,
               monitoring_status:int=None, second_responsible:int=None, task_status:int=None, expired:bool=None,start_period:str=None, end_period:str=None,
               user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = loan_case_get.get_all_loan_case_v2(size, page, region_id, local_code_id, loan_id, client_name, is_target,
                                                    product_type, client_type, task_status_id, lending_type, client_code, monitoring_stage, monitoring_status, 
                                                    second_responsible, task_status, expired, start_period, end_period, user,
                                                    user.department, db_session)
        
    return response