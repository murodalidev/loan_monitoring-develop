from datetime import datetime, timedelta, date
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ....models.loan_case.loan_case_model import LoanCase
from ....models.monitoring_case.monitoring_case_model import MonitoringCase
from ....models.loan_case.loan_case_history_model import LoanCaseHistory
from ....models.juridical_case.juridical_case_model import JuridicalCase
from ....models.problems_case.problems_case_model import ProblemsCase
from ....models.monitoring_task_manager.task_manager_model import TaskManager
from ....models.problems_case.problems_case_history import ProblemsCaseHistory
from ....models.problems_case.problems_monitoring_model import ProblemsMonitoring
from ....models.monitoring_case.target_monitoring_model import TargetMonitoring
from ....models.monitoring_case.scheduled_monitoring_model import ScheduledMonitoring
from ..general_tasks import general_tasks_crud
from ..task_manager.task_manager_crud import TaskManager_class
from ....models.juridical_case.juridical_case_history_model import JuridicalCaseHistory
from  app.services.loan_monitoring.problems_case import letters_crud
from  app.services.loan_monitoring.monitoring_case.script_date_holidays import get_business_days
from ..loan_case import loan_case_crud
from sqlalchemy import or_, and_, cast, Date
from ....models.brief_case.directories.loan_product import loan_product
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


def loan_case_send_to_problems(db_session):
    get_loan_cases = db_session.query(LoanCase).filter(LoanCase.loan_case_status_id != 4)\
        .filter(LoanCase.task_manager_id == TaskManager.id)\
                 .filter(and_(TaskManager.general_task_id != MGT.SEND_PORBLEM.value, TaskManager.general_task_id != MGT.SEND_JURIDIC.value, TaskManager.general_task_id != MGT.CLOSE.value)).all()
    i=0
    for loan in get_loan_cases:
        if loan.expired_status == True:
            is_target = db_session.query(loan_product).filter(loan_product.name == loan.portfolio.loan_product).first()
            if (loan.monitoring_case and loan.monitoring_case.target and loan.monitoring_case.target.target_monitoring_result_id is not None) or is_target.is_target == 0:
                i=i+1
                send_to_problems(loan, db_session)
    if i!=0:
        data = CreateNotification()
        data.from_user_id = None
        data.to_user_id = None
        data.notification_type = notification_dictionary.notification_type['problems']
        data.body = notification_dictionary.notification_body['send_to_problems']
        data.url = None
        notifiaction = Notificaton_class(data)
        notifiaction.create_notification(db_session)

        commit_object(db_session)
    
    return {"OK"}


def send_to_problems(loan, db_session):
    if check_if_problems_case_is_empty(loan.portfolio.id, db_session):
    
        new_problems_case = ProblemsCase(loan_portfolio_id = loan.portfolio.id,
                                        problems_case_status_id = problems_case['новый'],
                                        created_at = datetime.now())
        
        db_session.add(new_problems_case)
        flush_object(db_session)
        
        
        
        loan_case = db_session.query(LoanCase).filter(LoanCase.id == loan.id).first()
        
        data = UpdateTaskManagerSetResponsible()
        data.task_manager_id = loan_case.task_manager_id
        data.general_task_id = MGT.SEND_PORBLEM.value
        data.task_status = task_status['завершено']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
        
        
        new_loan_case_history = LoanCaseHistory(loan_case_id = loan_case.id, 
                                                general_task_id = MGT.SEND_PORBLEM.value,
                                                created_at = datetime.now(),
                                                message = loan_case_history['send_to_problem']
                                                    )
        db_session.add(new_loan_case_history)
        flush_object(db_session)
    
    return "OK"






def check_if_problems_case_is_empty(loan_portfolio_id, db_session):#used
    get_problems_case = db_session.query(ProblemsCase).filter(ProblemsCase.loan_portfolio_id == loan_portfolio_id)\
        .filter(ProblemsCase.problems_case_status_id != problems_case['закрыт']).first()
    if get_problems_case is not None:
        return False
    return True


def notify_about_dedline(db_session):
    today = datetime.today()
    dedline_day = get_business_days(datetime.today(), 15, db_session)
    get_target_monitoring = db_session.query(TargetMonitoring)\
        .filter(and_((cast(TargetMonitoring.deadline, Date) <= dedline_day),(cast(TargetMonitoring.deadline, Date) >= today)))\
        .filter(TargetMonitoring.target_monitoring_result_id == None).count()
    for target in get_target_monitoring:
        print((target.deadline - today).days, " days to target monitoring")
        second_responsible = db_session.query(LoanCase.second_responsible_id).filter(LoanCase.monitoring_case_id == MonitoringCase.id)\
            .filter(MonitoringCase.target_monitoring_id == TargetMonitoring.id).filter(TargetMonitoring.id == target.id).first()
        print("second_responsible ", second_responsible.second_responsible_id)
        data = CreateNotification()
        data.from_user_id = None
        data.to_user_id = second_responsible.second_responsible_id
        data.notification_type = notification_dictionary.notification_type['target_monitoring']
        data.body = f"До следующего мониторинга осталось {(target.deadline - today).days} день"
        data.url = None
        notifiaction = Notificaton_class(data)
        notifiaction.create_notification(db_session)
    
    
    get_scheduled_monitoring = db_session.query(ScheduledMonitoring)\
        .filter(and_((cast(ScheduledMonitoring.deadline, Date) <= dedline_day),(cast(ScheduledMonitoring.deadline, Date) >= today)))\
        .filter(ScheduledMonitoring.scheduled_monitoring_result_id == None).all()
    if get_scheduled_monitoring:
        for schedule in get_scheduled_monitoring:
            print((schedule.deadline - date.today()).days, " days to scheduled monitoring")
            second_responsible = db_session.query(LoanCase.second_responsible_id)\
                .filter(LoanCase.monitoring_case_id == ScheduledMonitoring.monitoring_case_id).first()
            print("second_responsible ", second_responsible.second_responsible_id)
            data = CreateNotification()
            data.from_user_id = None
            data.to_user_id = second_responsible.second_responsible_id
            data.notification_type = notification_dictionary.notification_type['scheduled_monitoring']
            data.body = f"До следующего планового мониторинга осталось {(schedule.deadline - date.today()).days} день"
            data.url = None
            notifiaction = Notificaton_class(data)
            notifiaction.create_notification(db_session)
    
    commit_object(db_session)
    
    return "OK"
