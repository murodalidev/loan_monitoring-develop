from fastapi import APIRouter, Depends, BackgroundTasks
from app.db.connect_db import SessionManager
from ...services.loan_monitoring.integrations import soliq_integrations
from ...schemas.integrations import Soliq_eauksion_orders, Soliq_eauksion_order, Soliq_eauksion_orders_repotr
from ...config.logs_config import info_logger
from app.middleware.auth_file import AuthHandler
from ...services.reports.eauksion_report import create_report_to_excel

auth_handler = AuthHandler()



router = APIRouter(
    prefix = "/integrations", tags=["Soliq"]
)

@router.get('/soliq/v1/form1')
def form1(inn: str, year: int, period: int, loan_portfolio_id:int, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = soliq_integrations.bux_balance_first_form(inn, year, period, loan_portfolio_id, user.id, db_session)
    info_logger.info("User %s requested bux balance by form1", user.id)
    
    return response

@router.get('/soliq/v1/form2')
def form2(inn: str, year: int, period: int,loan_portfolio_id:int, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = soliq_integrations.bux_balance_second_form(inn, year, period, loan_portfolio_id, user.id, db_session)
    info_logger.info("User %s requested bux balance by form1", user.id)
    
    return response


@router.post('/soliq/v1/eauksion/get-orders')
def get_eauksion_orders(request:Soliq_eauksion_orders, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = soliq_integrations.get_eauksion_orders(request, user.id, db_session)
    info_logger.info("User %s requested eauksion get-orders", user.id)
    
    return response



@router.post('/soliq/v1/eauksion/get-order-info')
def get_eauksion_order_info(request:Soliq_eauksion_order, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = soliq_integrations.get_eauksion_order_info(request, user.id, db_session)
    info_logger.info("User %s requested eauksion get-order-info", user.id)
    
    return response


@router.post('/soliq/v1/eauksion/get-orders/report')
def get_eauksion_orders(request:Soliq_eauksion_orders_repotr, back_task: BackgroundTasks, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        back_task.add_task(create_report_to_excel, request, user.id, db_session)
    info_logger.info("User %s requested eauksion get-orders", user.id)
    return 'Отчет появится через некоторое время'