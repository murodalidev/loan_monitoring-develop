from fastapi import APIRouter, Depends
from app.db.connect_db import SessionManager
from ...services.loan_monitoring.integrations import logs
from ...schemas.integrations import MIB_debtors_info
from ...config.logs_config import info_logger
from app.middleware.auth_file import AuthHandler

auth_handler = AuthHandler()



router = APIRouter(
    prefix = "/integrations/log", tags=["integrations log"]
)

@router.get('/v1/get')
def get_history(size:int, page:int, service_api_id:int, loan_portfolio_id:int=None):
    with SessionManager() as db_session:
        response = logs.get_log(size, page, service_api_id, loan_portfolio_id, db_session)
    return response


@router.get('/v1/service_api_list')
def get_api_list():
    with SessionManager() as db_session:
        response = logs.get_service_api_list(db_session)    
    return response