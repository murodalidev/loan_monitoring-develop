from fastapi import APIRouter, Depends
from app.db.connect_db import SessionManager
from fastapi import BackgroundTasks
from ....services.loan_monitoring.loan_porfolio.loan_portfolio_service import load_portfolio
from ....services.loan_monitoring.loan_porfolio import check_loan_portfolio
from ....services.loan_monitoring.loan_porfolio import loan_portfolio_auto_distribution, back_loan_to_user
from ....services.loan_monitoring.loan_porfolio.auto_distribution import business_distribution, kad_distribution, problem_distribution
from ....services.loan_monitoring.loan_porfolio.update_loan_portfolio_service import update_portfolio, uncheck_portfolio_data, closed_portfolio_data, portfolio_update_full, get_portfolio_data
import logging
logger = logging.getLogger(__name__)
router = APIRouter(
    prefix = "/portfolio", tags=["Loan Porfolio"]
)

@router.post('/v1/load/all')
def portrfolio(back_task: BackgroundTasks):
    with SessionManager() as db_session:
         back_task.add_task(load_portfolio, db_session)
    return {'OK'}


@router.post('/v1/update/all')
def portrfolio(back_task: BackgroundTasks, date:str=None):
    with SessionManager() as db_session:
        back_task.add_task(update_portfolio, date, db_session)
    return {'OK'}

@router.post('/v1/uncheck/all')
def portrfolio(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        back_task.add_task(uncheck_portfolio_data, db_session)
        #uncheck_portfolio_data(db_session)
    return {'OK'}

@router.post('/v1/closed-loan/all')
def portrfolio(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        back_task.add_task(closed_portfolio_data, db_session)
        #closed_portfolio_data(db_session)
    return {'OK'}

@router.post('/v1/update/full')
def update_full(back_task: BackgroundTasks, date:str=None):
    with SessionManager() as db_session:
        back_task.add_task(portfolio_update_full, date, db_session)
    return {'OK'}


@router.get('/v1/get-portfolio-date')
def portrfolio_get_date():
    with SessionManager() as db_session:
        return get_portfolio_data(db_session)
    return {'OK'}


@router.post('/v1/check-expiration/all')
def portrfolio(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        back_task.add_task(check_loan_portfolio.loan_porfolio_check_expiration, db_session)
        #check_loan_portfolio.loan_porfolio_check_expiration(db_session)
    return {'OK'}


@router.get('/v1/distribution')
def portrfolio_distribution(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        back_task.add_task(loan_portfolio_auto_distribution.portfolio_auto_distribution,db_session)
    return {'OK'}



@router.get('/v1/distribution/by-local')
def portrfolio_distribution_by_local(back_task: BackgroundTasks, is_new_local:int=None):
    with SessionManager() as db_session:
        back_task.add_task(loan_portfolio_auto_distribution.portfolio_auto_distribution_by_local,db_session, is_new_local)
    return {'OK'}


@router.get('/v1/check-loan-case-with-product-change')
def portrfolio_distribution_by_local(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        back_task.add_task(loan_portfolio_auto_distribution.check_loan_case_with_product_change,db_session)
    return {'OK'}


@router.get('/v1/give-back-loans-to-users')
def portrfolio_distribution_by_local(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        back_task.add_task(back_loan_to_user.gateway_to_back,db_session)
    return {'OK'}


@router.get('/v1/distribution/by-local/all')
def portrfolio_distribution_by_local(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        back_task.add_task(business_distribution.auto_distribution_all,db_session)
    return {'OK'}


@router.get('/v1/distribution-to-business/by-local')
def portrfolio_distribution_by_local_local(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        # back_task.add_task(business_distribution.portfolio_auto_distribution_by_local_to_businessv1,db_session)
        business_distribution.portfolio_auto_distribution_by_local_to_businessv1(db_session)
    return {'OK'}


@router.get('/v1/distribution-to-kad/by-local')
def portrfolio_distribution_by_local_kad(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        #back_task.add_task(kad_distribution.portfolio_auto_distribution_by_local_to_kad,db_session)
        kad_distribution.portfolio_auto_distribution_by_local_to_kad(db_session)
    return {'OK'}



@router.get('/v1/distribution-to-problem/by-local')
def portrfolio_distribution_by_local_problem(back_task: BackgroundTasks):
    with SessionManager() as db_session:
        #back_task.add_task(kad_distribution.portfolio_auto_distribution_by_local_to_kad,db_session)
        problem_distribution.portfolio_auto_distribution_by_local_to_problemv1(db_session)
    return {'OK'}