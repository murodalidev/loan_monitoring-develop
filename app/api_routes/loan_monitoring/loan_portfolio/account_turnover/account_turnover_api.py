from fastapi import APIRouter
from app.db.connect_db import SessionManager
from app.db.oracle_connect import OracleSessionManager
from fastapi import BackgroundTasks
from .....services.loan_monitoring.loan_porfolio.account_turnover import account_turnover_service
import logging
logger = logging.getLogger(__name__)
router = APIRouter(
    prefix = "/account_turnover", tags=["Account Turnover"]
)

@router.get('/v1/load/accounts')
def load_all_accounts(back_task: BackgroundTasks, day:int=None):
    with OracleSessionManager() as orc_session:
        with SessionManager() as db_session:
            back_task.add_task(account_turnover_service.load_accounts,orc_session, day, db_session)
    return "OK"



@router.get('/v1/load-debt-account-start-state-and-repayment-date')
def load_loans_to_balance_turnover(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        back_task.add_task(account_turnover_service.turnover_load_debt_account_16377_start_state_and_repayment_date, db_session)
    return "OK"

@router.get('/v1/163XX-accounts-start-state')
def accounts_163XX_start_state(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        #back_task.add_task(account_turnover_service.turnover_163XX_accounts_start_state,db_session)
        account_turnover_service.turnover_163XX_accounts_start_state(db_session)
    return "OK"


@router.get('/v1/95413-9150x-accounts-start-state')
def accounts_163XX_start_state(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        back_task.add_task(account_turnover_service.turnover_95413_and_9150x_accounts_start_state,db_session)
    return "OK"


# @router.get('/v1/load-account-16377-start-state')
# def load_loans_to_balance_turnover(back_task: BackgroundTasks):
#     with SessionManager() as db_session:
#         back_task.add_task(account_turnover_service.turnover_load_account_16377_start_state,db_session)
#     return "OK"


@router.get('/v1/unchek-balance-turnover-update')
def unchek_balance_turnover(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        back_task.add_task(account_turnover_service.unchek_balance_turnover_update,db_session)
    return "OK"


# @router.get('/v1/load-repayment-date')
# def load_repayment_date():
#     with SessionManager() as db_session:
#         result = account_turnover_service.turnover_load_repayment_date(db_session)
#     return result


@router.get('/v1/all-credit-sums')
def main_accounts_credit_sums(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        back_task.add_task(account_turnover_service.all_turnover_account_update, db_session)
    return "OK"

@router.get('/v1/main-accounts-credit-sums')
def main_accounts_credit_sums(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        back_task.add_task(account_turnover_service.turnover_main_accounts_credit_sums, db_session)
    return "OK"


@router.get('/v1/16377-accounts-credit-debit-sums')
def accounts_16377_credit_debit_sums(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        back_task.add_task(account_turnover_service.turnover_16377_accounts_credit_debit_sums, db_session)
    return "OK"

@router.get('/v1/163XX-accounts-credit-debit-sums')
def accounts_163XX_credit_debit_sums(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        back_task.add_task(account_turnover_service.turnover_163XX_accounts_credit_debit_sums, db_session)
    return "OK"



@router.get('/v1/export-turnover-data-to-history')
def accounts_163XX_credit_debit_sums(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        back_task.add_task(account_turnover_service.export_balance_turnover_data_to_history, db_session)
    return "OK"


@router.get('/v1/last-oper-day')
def last_oper_day():
    with SessionManager() as db_session:
        oper_day = account_turnover_service.get_last_oper_day(db_session)
    return oper_day.oper_day

@router.get('/v1/last-portfolio-date')
def last_portfolio_date():
    with SessionManager() as db_session:
        oper_day = account_turnover_service.get_last_portfolio_day(db_session)
    return oper_day.date

# @router.get('/v1/export-turnover-data-to-history')
# def accounts_163XX_credit_debit_sums():
#     with SessionManager() as db_session:
#         account_turnover_service.export_balance_turnover_data_to_history(db_session)
#     return "OK"