from fastapi import APIRouter, Depends
from app.db.connect_db import SessionManager
from ...services.loan_monitoring.integrations import iabs_integrations
from app.db.oracle_connect import OracleSessionManager
from ...services.loan_monitoring.integrations import client_card
from fastapi import BackgroundTasks
from ...config.logs_config import info_logger
from app.middleware.auth_file import AuthHandler

auth_handler = AuthHandler()

router = APIRouter(
    prefix = "/integrations", tags=["IABS"]
)

@router.post('iabs/v1/auth_to_iabs')
def auth():
  response = iabs_integrations.iabs_integrations_auth()
  
  return response

@router.get('/iabs/v1/get_client_credit_by_loan_id')
def get_client_credit(loan_id:int, user=Depends(auth_handler.auth_wrapper)):
  with SessionManager() as db_session:
    response = iabs_integrations.get_client_credit(db_session, loan_id)
  info_logger.info("User %s requested client credit info by loanid", user.id)
  return response

@router.get('/iabs/v1/get_customer')
def get_customer_by_pinfl(pinfl: int, loan_portfolio_id: int):
  with SessionManager() as db_session:
    response = iabs_integrations.get_customer(db_session, pinfl, loan_portfolio_id)

  return response

@router.get('/iabs/v1/get_corporate_customer')
def get_corporate_customer_by_inn(inn: int, loan_portfolio_id: int):
  with SessionManager() as db_session:
    response = iabs_integrations.get_corporate_customer(db_session, inn, loan_portfolio_id)

  return response


@router.get('/iabs/v1/get-currency-rate')
def get_currency_rate():
  with SessionManager() as db_session:
    response = iabs_integrations.get_currency_rate(db_session)

  return response



@router.get('/iabs/v1/get_active_accounts/{clientUid}')
def get_accounts(client_uid: int, code_mfo: str):
  response = iabs_integrations.get_active_accounts(client_uid, code_mfo)

  return response 

@router.get('/iabs/v1/get_account_turnover_for_loan')
def get_accounts(account: str, code_mfo: str, date_begin: str, date_close: str):
  response = iabs_integrations.get_account_turnover_for_loan(account, code_mfo, date_begin, date_close)

  return response 

@router.get('/iabs/v1/loan-repayment-schedule')
def get_schedule(loan_id: str):
  with SessionManager() as db_session:
    response = iabs_integrations.get_loan_repayment_schedule(db_session, loan_id)

  return response 



@router.get('/v1/load/client-card')
def load_all_accounts():
    with OracleSessionManager() as orc_session:
      with SessionManager() as db_session:
            result = client_card.load_client_data(orc_session, db_session)
    return result
  
  
  
@router.get('/v1/load/schedules')
def load_schedules(back_task: BackgroundTasks):
    with OracleSessionManager() as orc_session:
      with SessionManager() as db_session:
        return client_card.load_loan_schedule(orc_session, db_session)
            #result = client_card.load_loan_schedule(orc_session, db_session)
    return "OK"