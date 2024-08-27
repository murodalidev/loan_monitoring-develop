from datetime import datetime, timedelta
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ....models.loan_case.loan_case_model import LoanCase
from ....models.loan_case.loan_case_history_model import LoanCaseHistory
from ....models.juridical_case.juridical_case_model import JuridicalCase
from ....models.problems_case.problems_case_model import ProblemsCase
from ....models.problems_case.problems_case_history import ProblemsCaseHistory
from ....models.problems_case.problems_monitoring_model import ProblemsMonitoring
from ..general_tasks import general_tasks_crud
from sqlalchemy import or_, and_
from ..loan_case import loan_case_crud
from ..task_manager.task_manager_crud import TaskManager_class
from ....models.monitoring_task_manager.task_manager_model import TaskManager
from ....models.juridical_case.juridical_case_history_model import JuridicalCaseHistory
from  app.services.loan_monitoring.problems_case import letters_crud
from  app.services.users.users_crud import Users as users
from ....common.commit import commit_object, flush_object
from ....common.is_empty import is_empty, is_exists
from ....schemas.task_manager_schemas import UpdateTaskManagerSetResponsible, UpdateTaskManagerClose,UpdateTaskManagerAccept
from ....schemas.notification_schemas import CreateNotification
from ....models.files.monitoring_files_model import MonitoringFiles
from ..notification.notification_crud import Notificaton_class
from ....common.dictionaries import notification_dictionary, task_status_dictionaries
from ....common.dictionaries.task_status_dictionaries import task_status
from ....common.dictionaries.monitoring_case_dictionary import problems_case, problems_monitoring, letter_status, juridic_case
from ....common.dictionaries.case_history_dictionaries import problem_case_history, loan_case_history, juridical_case_history
from ....common.dictionaries.departments_dictionary import DEP
from ....common.dictionaries.general_tasks_dictionary import JGT, MGT, PGT, GTCAT



def send_to_juridical_notification(db_session):
    today = datetime.now()    
    k=0
    n_days_ago = today - timedelta(days=14)#TODO: check if mail has sent
    get_problems_cases = db_session.query(ProblemsCase).filter(ProblemsCase.problems_case_status_id != 4)\
        .filter(ProblemsCase.main_responsible_id != None)\
            .filter(ProblemsMonitoring.id == ProblemsCase.problems_monitoring_id)\
                .filter(ProblemsCase.problems_monitoring_id != None)\
                .filter(ProblemsCaseLetters.problems_monitoring_id == ProblemsMonitoring.id)\
             .filter(ProblemsCase == TaskManager.id)\
                 .filter(and_(TaskManager.general_task_id != PGT.SEND_JURIDIC.value, TaskManager.general_task_id != PGT.REPAID.value)).all()
    
    for problem in get_problems_cases: 
        if check_expiration(n_days_ago, problem.portfolio):
            k=k+1
            set_task_to_juridical(problem, db_session)

    if k>0:
        data = CreateNotification()
        data.from_user_id = None
        data.to_user_id = None
        
        data.notification_type = notification_dictionary.notification_type['juridical']
        data.body = notification_dictionary.notification_body['send_to_juridical']
        data.url = None
        
        notifiaction = Notificaton_class(data)
        notifiaction.create_notification(db_session)

        commit_object(db_session)
    
    return {"OK"}


def check_expiration(n_days_ago, portfolio): #TODO:
    if (portfolio.overdue_start_date is not None) and (portfolio.date_overdue_percent is not None):
        if portfolio.overdue_start_date > portfolio.date_overdue_percent:
            if n_days_ago.date() > portfolio.date_overdue_percent:
                return True
        elif portfolio.overdue_start_date < portfolio.date_overdue_percent:
            if n_days_ago.date() > portfolio.overdue_start_date:
                return True
    elif portfolio.overdue_start_date is not None:
        if n_days_ago.date() > portfolio.overdue_start_date:
            return True
    elif  portfolio.date_overdue_percent is not None:
        if n_days_ago.date() > portfolio.date_overdue_percent:
            return True
    else:
        return False
            
            
            
            

def change_status(portfolio, expired_status, status, db_session):
    portfolio.status = status
    loan_case_crud.change_expired_status(portfolio.id, expired_status, db_session)
    
    
    
    
    
    
    
    
    
def set_task_to_juridical(problem_case, db_session):
    
    data = UpdateTaskManagerAccept()
    data.task_manager_id = problem_case.task_manager_id
    data.general_task_id = PGT.SEND_JURIDIC.value
    data.task_status = task_status['впроцессе']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
        
    flush_object(db_session)
    
    return {"OK"}



def check_if_juridical_case_has_not_set(loan_portfolio_id, db_session):#used
    
    juridical_case = db_session.query(JuridicalCase)\
            .filter(JuridicalCase.loan_portfolio_id == loan_portfolio_id)\
            .filter(JuridicalCase.juridical_case_status_id != juridic_case['закрыт']).first()
    is_empty(juridical_case, 400,f'Juridical case has already appended to user.')