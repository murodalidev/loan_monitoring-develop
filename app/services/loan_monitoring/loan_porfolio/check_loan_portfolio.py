from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ....models.loan_case.loan_case_model import LoanCase
from ....models.problems_case.problems_case_model import ProblemsCase
from ....models.juridical_case.juridical_case_model import JuridicalCase
from ....models.monitoring_task_manager.task_manager_model import TaskManager
from ....schemas.notification_schemas import CreateNotification
from ..notification.notification_crud import Notificaton_class
from ....common.dictionaries import notification_dictionary
from ..loan_case import loan_case_crud
from ..directories.load_all_from_files import get_directories
from ....common.commit import commit_object, flush_object
from ....common.is_empty import is_empty, is_empty_list

def loan_porfolio_check_expiration(db_session):
    today = datetime.now()    
    n_days_ago = today - timedelta(days=31)
    get_loan_portfolios = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.status != 3).all()
    
    for portfolio in get_loan_portfolios: 
        check_expiration(n_days_ago, portfolio, db_session)
           
    commit_object(db_session)
    
    


def check_expiration(n_days_ago, portfolio, db_session): #TODO:
    if (portfolio.overdue_start_date is not None) and (portfolio.date_overdue_percent is not None):
        if portfolio.overdue_start_date > portfolio.date_overdue_percent:#TODO optimize
            if n_days_ago.date() > portfolio.date_overdue_percent and portfolio.is_taken_problem == False and portfolio.is_taken_juridic == False:
                change_status(portfolio, True, 1, db_session)
        elif portfolio.overdue_start_date < portfolio.date_overdue_percent:
            if n_days_ago.date() > portfolio.overdue_start_date and portfolio.is_taken_problem == False and portfolio.is_taken_juridic == False:
                change_status(portfolio, True, 1, db_session)
    elif portfolio.overdue_start_date is not None:
        if n_days_ago.date() > portfolio.overdue_start_date and portfolio.is_taken_problem == False and portfolio.is_taken_juridic == False:
            change_status(portfolio, True, 1, db_session)
    elif  portfolio.date_overdue_percent is not None:
        if n_days_ago.date() > portfolio.date_overdue_percent and portfolio.is_taken_problem == False and portfolio.is_taken_juridic == False:
            change_status(portfolio, True, 1, db_session)
            
    elif portfolio.overdue_start_date is None and portfolio.date_overdue_percent is None and (portfolio.is_taken_problem == True or portfolio.is_taken_juridic == True):
        change_status(portfolio, False, 2, db_session)
        send_notification(portfolio, db_session)#TODO: переделать!
    elif portfolio.overdue_start_date is None and portfolio.date_overdue_percent is None:
        change_status(portfolio, False, 2, db_session)
        send_notification(portfolio, db_session)
        


def change_status(portfolio, expired_status, status, db_session):
    portfolio.status = status
    loan_case_crud.change_expired_status(portfolio.id, expired_status, db_session)
        
        
        
def send_notification(case, db_session):
    get_problems_case = db_session.query(ProblemsCase).filter(ProblemsCase.loan_portfolio_id == case.id)\
        .filter(ProblemsCase.problems_case_status_id != 4).first()
    if get_problems_case is not None:
        data = CreateNotification()
        data.from_user_id = None
        data.to_user_id = get_problems_case.main_responsible_id
        data.notification_type = notification_dictionary.notification_type['problems']
        data.body = notification_dictionary.notification_body['client_repaid']
        data.url = notification_dictionary.notification_url['problems_monitoring']+':'+ f'{get_problems_case.id}'
        notifiaction = Notificaton_class(data)
        notifiaction.create_notification(db_session)