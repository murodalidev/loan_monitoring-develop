from fastapi import APIRouter, Depends
from app.db.connect_db import SessionManager
from ....services.loan_monitoring.monitoring_case import monitoring_case_crud
from app.middleware.auth_file import AuthHandler
from ....common import common_handler
auth_handler = AuthHandler()


router = APIRouter(
    prefix = "/monitoring-case", tags=["Monitoring Case"]
)


@router.get('/v1/get/detail')
def get_monitoring_case_detail(monitoring_case_id:int, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = common_handler.handle_error(monitoring_case_crud.get_monitoring_case, user.id, monitoring_case_id, db_session)
    return response


@router.get('/v1/get/all')
def get_all_case_monitoring(page:int, size:int, region_id:int=None, local_code_id:int=None, client_code:int=None, loan_id:int=None, client_name:str=None, is_target:int=None,
               client_type:str=None, main_responsible:int=None, second_responsible:int=None, monitoring_status:int=None, task_status:int=None, lending_type:str=None,
               user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = common_handler.handle_error(monitoring_case_crud.get_all_monitoring,page, size, region_id, local_code_id, client_code, loan_id,
                                                           client_name, is_target, client_type,
                                                           main_responsible, second_responsible,
                                                           monitoring_status, task_status, lending_type,
                                                           user, db_session)
    return response
