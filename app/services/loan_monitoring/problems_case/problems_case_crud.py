from datetime import datetime, timedelta

from app.models.problems_case.auction.auction_model import ProblemsAuction
from app.models.problems_case.judicial_process.judicial_process_data_model import JudicialData
from app.models.problems_case.mib_ended.mib_model import ProblemsMib
from app.models.problems_case.out_of_balance.out_of_balance_model import OutOfBalance
from app.models.problems_case.problems_assets.problems_assets_model import ProblemsAssets
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ....models.loan_case.loan_case_model import LoanCase
from ....models.loan_case.loan_case_history_model import LoanCaseHistory
from ....models.juridical_case.juridical_case_model import JuridicalCase
from ....models.problems_case.problems_case_model import ProblemsCase
from ....models.problems_case.problems_case_history import ProblemsCaseHistory
from ....models.problems_case.problems_monitoring_model import ProblemsMonitoring
from app.models.problems_case.problem_state_chain_model import ProblemStateChain
from app.models.problems_case.problem_states_model import ProblemStates
from ..general_tasks import general_tasks_crud
from ..task_manager.task_manager_crud import TaskManager_class
from ....models.juridical_case.juridical_case_history_model import JuridicalCaseHistory
from  app.services.loan_monitoring.problems_case import letters_crud
from  app.services.users.users_crud import Users as users
from ....common.commit import commit_object, flush_object
from ....common.is_empty import is_empty, is_exists, is_empty_list
from ....schemas.task_manager_schemas import UpdateTaskManagerSetResponsible, UpdateTaskManagerClose,UpdateTaskManagerAccept
from ....schemas.notification_schemas import CreateNotification
from ....models.files.monitoring_files_model import MonitoringFiles
from ..notification.notification_crud import Notificaton_class
from ....common.dictionaries import notification_dictionary, task_status_dictionaries
from ....common.dictionaries.task_status_dictionaries import task_status
from ....common.dictionaries.monitoring_case_dictionary import monitoring_status
from ....common.dictionaries.monitoring_case_dictionary import problems_case, problems_monitoring, letter_status, juridic_case
from ....common.dictionaries.case_history_dictionaries import problem_case_history, loan_case_history, juridical_case_history
from ....common.dictionaries.departments_dictionary import DEP
from ....common.dictionaries.general_tasks_dictionary import JGT, KGT, MGT, PGT, GTCAT
from ....common.dictionaries.monitoring_case_dictionary import loan_case
from ....models.users.users import Users as users_model
from sqlalchemy.orm import aliased
from sqlalchemy import case, and_, or_
from sqlalchemy.sql.expression import cast, extract
from sqlalchemy.sql import func, text
import sqlalchemy
from ....models.brief_case.loan_portfolio_schedule import LoanPortfolioSchedule
from ....models.statuses.problems_case_status_model import ProblemsCaseStatus
from ....models.brief_case.directories.bank_mfo import bank_mfo
from ....models.brief_case.directories.local_code import local_code
from ....models.brief_case.directories.client_region import client_region
from ....models.brief_case.directories.currency import currency
from ....models.monitoring_task_manager.task_manager_model import TaskManager
from ....models.brief_case.directories.loan_product import loan_product

def send_to_problems(request, db_session):
    check_if_problems_case_is_empty(request.loan_portfolio_id, db_session)
    
    new_problems_case = ProblemsCase(loan_portfolio_id = request.loan_portfolio_id,
                                     problems_case_status_id = problems_case['новый'],
                                     created_at = datetime.datetime.now())
    
    db_session.add(new_problems_case)
    flush_object(db_session)
    
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = None
    data.notification_type = notification_dictionary.notification_type['problems']
    data.body = notification_dictionary.notification_body['send_to_problems']
    data.url = None
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    loan_case = db_session.query(LoanCase).filter(LoanCase.id == request.loan_case_id).first()
    
    data = UpdateTaskManagerSetResponsible()
    data.task_manager_id = loan_case.task_manager_id
    data.general_task_id = request.general_task_id
    data.task_status = task_status['завершено']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    
    
    new_loan_case_history = LoanCaseHistory(loan_case_id = loan_case.id, 
                                            general_task_id = request.general_task_id,
                                            from_user_id = request.from_user,
                                            created_at = datetime.datetime.now(),
                                            message = loan_case_history['send_to_problem']
                                                )
    db_session.add(new_loan_case_history)
    commit_object(db_session)
    user = users.get_user_by_department(6,db_session)
    
    return user







def reply_to_new_juridical_case(request, file_path, db_session):
    juridical_case = db_session.query(JuridicalCase).filter(JuridicalCase.loan_portfolio_id == request.loan_portfolio_id)\
        .filter(JuridicalCase.juridical_case_status_id == juridic_case['новый']).first()
        
    data = UpdateTaskManagerAccept()
    data.task_manager_id = juridical_case.task_manager_id
    data.task_status = task_status['на проверку']
    task = TaskManager_class(data)
    juridic_task = task.update_task_manager(db_session)
    
    new_juridical_case_history = JuridicalCaseHistory(juridical_case_id = juridical_case.id, 
                                                general_task_id = JGT.COORDINATE_DOCUMENTS,
                                                from_user_id = request.from_user,
                                                created_at = datetime.datetime.now(),
                                                to_user_id = juridical_case.main_responsible_id,
                                                comment = request.comment,
                                                message = juridical_case_history['reply_to_new_loan'],
                                                )
    db_session.add(new_juridical_case_history)
    flush_object(db_session)
    
    
    
    
    case = db_session.query(ProblemsCase).filter(ProblemsCase.id == request.case_id).first()
        
    data = UpdateTaskManagerAccept()
    data.task_manager_id = case.task_manager_id
    data.task_status = task_status['на проверку']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    
    
    
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = juridical_case.main_responsible_id
    data.notification_type = notification_dictionary.notification_type["juridical"]
    data.body = notification_dictionary.notification_body['new_reply_from_problem']
    data.url = f'{juridical_case.loan_portfolio_id}'+':'+ f'{juridical_case.id}'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)

    
    new_problems_case_history = ProblemsCaseHistory(problems_case_id = request.case_id, general_task_id = request.general_task_id,
                                                from_user_id = request.from_user, created_at = datetime.datetime.now(),
                                                comment = request.comment,
                                                message = problem_case_history['send_to_juridical'],
                                                )
    db_session.add(new_problems_case_history)


    for path in file_path:
        new_file = MonitoringFiles(file_url = path, created_at = datetime.datetime.now())
        db_session.add(new_file)
        flush_object(db_session)
        juridical_case.files.append(new_file)
        db_session.add(juridical_case)
        new_juridical_case_history.files.append(new_file)
        db_session.add(new_juridical_case_history)
        new_problems_case_history.files.append(new_file)
        db_session.add(new_problems_case_history)
    commit_object(db_session)
    
    return juridical_case.main_responsible_id







def check_if_problems_case_is_empty(loan_portfolio_id, db_session):#used
    get_problems_case = db_session.query(ProblemsCase).filter(ProblemsCase.loan_portfolio_id == loan_portfolio_id)\
        .filter(ProblemsCase.problems_case_status_id != problems_case['закрыт']).first()
    is_empty(get_problems_case, 400,'Loan problem have already appended.') 
    return get_problems_case

def check_if_non_target_doesnt_exist(loan_portfolio_id, db_session):#used
    get_problems_case = db_session.query(ProblemsCase).join(Loan_Portfolio, Loan_Portfolio.id==loan_portfolio_id)\
        .filter(Loan_Portfolio.is_taken_non_target==True)\
        .filter(ProblemsCase.problems_case_status_id != problems_case['закрыт']).first()
    is_empty(get_problems_case, 400,'Non target has already appended.') 
    return get_problems_case

    
def check_if_problems_case_has_no_responsible(request, db_session):#used
    for accept in request.accept:
        get_problems_case = db_session.query(ProblemsCase)\
            .filter(ProblemsCase.loan_portfolio_id == accept)\
            .filter(ProblemsCase.main_responsible_id == None).first()
        is_exists(get_problems_case, 400,'Problem case has already appended to user.')

def check_if_problems_list_case_has_no_responsible(accept, db_session):#used
    portfolios = []
    for portfolio in accept:
        portfolios.append(portfolio.loan_portfolio_id)
    get_problems_case = db_session.query(ProblemsCase)\
        .filter(ProblemsCase.loan_portfolio_id.in_(portfolios and portfolios or ()))\
        .filter(ProblemsCase.main_responsible_id != None).all()
    is_empty_list(get_problems_case, 400,'Problem cases has already appended to user.')

def update_problems_case_set_responsible(new_task, loan_portfolio_id, responsible_id, db_session):#used
    get_problems_case = db_session.query(ProblemsCase)\
        .filter(ProblemsCase.loan_portfolio_id == loan_portfolio_id)\
            .filter(ProblemsCase.problems_case_status_id == problems_case['новый']).first()
    get_problems_case.main_responsible_id = responsible_id
    get_problems_case.task_manager_id = new_task.id
    return get_problems_case


def check_if_problems_monitoring_has_no_responsible(problems_case_id, db_session):#used
    get_problems_case = db_session.query(ProblemsCase)\
        .filter(ProblemsCase.id == problems_case_id)\
            .filter(ProblemsCase.second_responsible_id == None).first()
    is_exists(get_problems_case, 400,'Problem case has already second responsbile.')
    return get_problems_case






def appoint_responsible_for_problems_monitoring(request, db_session):
    problems_case = check_if_problems_monitoring_has_no_responsible(request.problems_case_id, db_session)
    
    new_problems_monitoring = ProblemsMonitoring(problems_monitoring_status_id = problems_monitoring['новый'],
                                                 created_at = datetime.datetime.now())
    db_session.add(new_problems_monitoring)
    flush_object(db_session)
    
    problems_case.second_responsible_id = request.to_user
    problems_case.updated_at = datetime.datetime.now()
    problems_case.problems_monitoring_id = new_problems_monitoring.id
    
    
    data = UpdateTaskManagerSetResponsible()
    data.task_manager_id = problems_case.task_manager_id
    data.general_task_id = request.general_task_id
    data.task_status = task_status['завершено']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    
      
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = request.to_user
    data.notification_type = notification_dictionary.notification_type['problems']
    data.body = notification_dictionary.notification_body['problems_monitoring_appoint']
    data.url = f'{problems_case.loan_portfolio_id}'+':'+ f'{problems_case.id}'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    
    new_problem_case_history = ProblemsCaseHistory(problems_case_id = problems_case.id, 
                                            general_task_id = request.general_task_id,
                                            from_user_id = request.from_user,
                                            to_user_id = request.to_user,
                                            created_at = datetime.datetime.now(),
                                            message = problem_case_history['appoint_responsible']
                                                )
    db_session.add(new_problem_case_history)
    commit_object(db_session)
    
    return "OK"
    


def appoint_second_responsible_for_problems_monitoring_list(problems_case_obj, from_user, second_responsible_id, general_task_id,  db_session):
    
    new_problems_monitoring = ProblemsMonitoring(problems_monitoring_status_id = problems_monitoring['новый'],
                                                 created_at = datetime.datetime.now())
    db_session.add(new_problems_monitoring)
    flush_object(db_session)
    
    problems_case_obj.second_responsible_id = second_responsible_id
    problems_case_obj.updated_at = datetime.datetime.now()
    problems_case_obj.problems_monitoring_id = new_problems_monitoring.id
    
    
    data = UpdateTaskManagerSetResponsible()
    data.task_manager_id = problems_case_obj.task_manager_id
    data.general_task_id = general_task_id
    data.task_status = task_status['завершено']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    
    new_problem_case_history = ProblemsCaseHistory(problems_case_id = problems_case_obj.id, 
                                            general_task_id = general_task_id,
                                            from_user_id = from_user,
                                            to_user_id = second_responsible_id,
                                            created_at = datetime.datetime.now(),
                                            message = problem_case_history['appoint_responsible']
                                                )
    db_session.add(new_problem_case_history)
    flush_object(db_session)
    
    return "OK"






    
def close_problems_case(request, db_session):
    #letters_crud.update_letter_set_repaid_true(request.problems_letter_id, db_session)
    update_problems_monitoring_set_isrepaid_true(request.problems_monitoring_id, db_session)
    prob_case = update_problems_case_set_status_closed(request.problems_case_id, db_session)
    
    data = UpdateTaskManagerClose()
    data.task_manager_id = prob_case.task_manager_id
    data.general_task_id = request.general_task_id
    data.task_status = task_status['завершено']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    
    
    loan_case = db_session.query(LoanCase).filter(LoanCase.loan_portfolio_id == prob_case.loan_portfolio_id).first()
    data = UpdateTaskManagerClose()
    data.task_manager_id =loan_case and loan_case.task_manager_id or None
    data.general_task_id = task_status_dictionaries.general_task_status['В работе']
    data.task_status = task_status['завершено']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    flush_object(db_session)
    
    
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = loan_case.main_responsible_id
    data.notification_type = notification_dictionary.notification_type['monitoring']
    data.body = notification_dictionary.notification_body['problems_closed']
    data.url = f'{loan_case.loan_portfolio_id}'+':'+ f'{loan_case.id}'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    loan_portfolio = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.id == prob_case.loan_portfolio_id).first()
    loan_portfolio.is_taken_problem = False
    
    commit_object(db_session)
    
    return loan_case.main_responsible_id



def close_problems_casev2(request, db_session):
    #letters_crud.update_letter_set_repaid_true(request.problems_letter_id, db_session)
    update_problems_monitoring_set_isrepaid_true(request.problems_monitoring_id, db_session)
    prob_case = update_problems_case_set_status_closed(request.problems_case_id, db_session)
    
    data = UpdateTaskManagerClose()
    data.task_manager_id = prob_case.task_manager_id
    data.general_task_id = request.general_task_id
    data.task_status = task_status['завершено']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    
    
    loan_case = db_session.query(LoanCase).filter(LoanCase.loan_portfolio_id == prob_case.loan_portfolio_id).first()
    data = UpdateTaskManagerClose()
    data.task_manager_id =loan_case and loan_case.task_manager_id or None
    data.general_task_id = task_status_dictionaries.general_task_status['В работе']
    data.task_status = task_status['завершено']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    flush_object(db_session)
    
    
    data = CreateNotification()
    data.from_user_id = request.from_user
    data.to_user_id = loan_case.main_responsible_id
    data.notification_type = notification_dictionary.notification_type['monitoring']
    data.body = notification_dictionary.notification_body['problems_closed']
    data.url = f'{loan_case.loan_portfolio_id}'+':'+ f'{loan_case.id}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    loan_portfolio = db_session.query(Loan_Portfolio).filter(Loan_Portfolio.id == request.loan_portfolio_id).first()
    loan_portfolio.is_taken_problem = False
    commit_object(db_session)
    
    return loan_case.main_responsible_id





    

def update_problems_monitoring_set_isrepaid_true(problems_monitoring_id, db_session):#used
    problems_monit = db_session.query(ProblemsMonitoring).filter(ProblemsMonitoring.id == problems_monitoring_id).first()
    
    problems_monit.is_repaid = True
    problems_monit.problems_monitoring_status_id = problems_monitoring['закрыт']
    problems_monit.updated_at = datetime.now()
    flush_object(db_session)
    return problems_monit
    
    
    
def update_problems_case_set_status_closed(problems_case_id, db_session):#used
    prob_case = db_session.query(ProblemsCase).filter(ProblemsCase.id ==problems_case_id).first()
    prob_case.problems_case_status_id = problems_case['закрыт']
    prob_case.updated_at = datetime.now()
    flush_object(db_session)
    return prob_case

def update_problems_case_set_status_waiting(problems_case_id, db_session):
    prob_case = db_session.query(ProblemsCase).filter(ProblemsCase.id ==problems_case_id).first()
    prob_case.problems_case_status_id = problems_case['ожидание']
    prob_case.updated_at = datetime.now()
    flush_object(db_session)
    return prob_case
    
    
    
    
def get_problems_case_history(problems_case_id,general_task_id, db_session):
    case_history = []
    
    problems_case_history = db_session.query(ProblemsCaseHistory).filter(ProblemsCaseHistory.general_task_id == general_task_id)\
        .filter(ProblemsCaseHistory.problems_case_id == problems_case_id).all()
    
    
    for history in problems_case_history:
        from_user =  users.get_user_by_id(history.from_user_id, db_session)
        to_user = users.get_user_by_id(history.to_user_id, db_session)
        case_history.append({"id":history.id,
                             "from_user": from_user,
                             "to_user": to_user,
                             "created_at": history.created_at,
                             "updated_at": history.updated_at,
                             "comment": history.comment,
                             "message": history.message,
                             "additional_data": history.additional_data,
                             "files": history.files and history.files})
        
    return case_history



def get_problems_monitoring(problems_monitoring_id, db_session):
    monitoring = []
    
    problems_monitoring = db_session.query(ProblemsMonitoring).filter(ProblemsMonitoring.id == problems_monitoring_id).first()
    
    letters = letters_crud.get_letters_by_monitoring_id(problems_monitoring_id, db_session)
    monitoring.append({"id":problems_monitoring.id,
                       "is_repaid": problems_monitoring.is_repaid and problems_monitoring.is_repaid  or None,
                       "arrival_of_property_id": problems_monitoring.arrival_of_property_id,
                       "management_agreement_id": problems_monitoring.management_agreement_id,
                       "problems_monitoring_status_id": problems_monitoring.problems_monitoring_status_id,
                       "created_at": problems_monitoring.created_at,
                       "updated_at": problems_monitoring.updated_at,
                       "letters": problems_monitoring.letters and letters})
        
    return monitoring
    
    
def create_problems_case_with_append_task(task, data, from_type, db_session):#used
    new_loan_case = ProblemsCase(loan_portfolio_id = data.loan_portfolio_id,
                                 main_responsible_id = data.main_responsible_id,
                                 deadline_extension_status_id = 1,
                                 second_responsible_id = data.second_responsible_id,
                                 problems_case_status_id = loan_case['Новый'],
                                 from_type_id = from_type,
                                 task_manager_id = task.id,
                                 created_at = datetime.now(),
                                 updated_at = datetime.now()
                                 )
    db_session.add(new_loan_case)
    flush_object(db_session)
    return new_loan_case



def get_all_problems_case(size, page, region_id, local_code_id, loan_id, client_name, is_target, task_status, product_type, state_chain, client_type, \
    client_code, currency_id, main_responsible, user, second_responsible, department, db_session):
    
    user_roles = []
    for role in user.roles:
        user_roles.append(role.name)
    
    
    main_user = aliased(users_model)
    second_user = aliased(users_model)
    loan_portfolio2 = aliased(Loan_Portfolio)
   
            
    period = datetime.today()
    overdue_max_date_case = case(
                        [
                            (and_(Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.date_overdue_percent != None,
                                  Loan_Portfolio.overdue_start_date <= Loan_Portfolio.date_overdue_percent), Loan_Portfolio.overdue_start_date),
                            (and_(Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.date_overdue_percent != None,
                                  Loan_Portfolio.overdue_start_date > Loan_Portfolio.date_overdue_percent), Loan_Portfolio.date_overdue_percent),
                           (and_(Loan_Portfolio.overdue_start_date != None, Loan_Portfolio.date_overdue_percent == None), Loan_Portfolio.overdue_start_date),
                           (and_(Loan_Portfolio.overdue_start_date == None, Loan_Portfolio.date_overdue_percent != None), Loan_Portfolio.date_overdue_percent)
                        ], else_=None).label("overdue_max_date")
    all_duty = case([
        (and_(Loan_Portfolio.overdue_balance != None, Loan_Portfolio.balance_16377 != None), 
         cast(Loan_Portfolio.overdue_balance, sqlalchemy.FLOAT) + cast(Loan_Portfolio.balance_16377, sqlalchemy.FLOAT)),
        (and_(Loan_Portfolio.overdue_balance != None, Loan_Portfolio.balance_16377 == None), 
         cast(Loan_Portfolio.overdue_balance, sqlalchemy.FLOAT)),
        (and_(Loan_Portfolio.overdue_balance == None, Loan_Portfolio.balance_16377 != None), 
         cast(Loan_Portfolio.balance_16377, sqlalchemy.FLOAT)),
        ], else_=None).label('all_duty')
    
    schedule_sum = case([(func.sum(cast(LoanPortfolioSchedule.summ_red, sqlalchemy.FLOAT)/100)==None, 0)], \
        else_=func.sum(cast(LoanPortfolioSchedule.summ_red, sqlalchemy.FLOAT)/100)).label('schedule_sum')
    
    sub_query_schedule_sum = db_session.query(schedule_sum).join(loan_portfolio2, loan_portfolio2.loan_id==LoanPortfolioSchedule.loan_id, isouter=True)\
        .filter(loan_portfolio2.loan_id==Loan_Portfolio.loan_id)\
        .filter(loan_portfolio2.status==1)\
            .filter(LoanPortfolioSchedule.date_red>=datetime.now()).scalar_subquery()
        
    
    # sub_query_schedule_date = db_session.query(func.max(LoanPortfolioSchedule.date_red))\
    #     .join(loan_portfolio3 ,LoanPortfolioSchedule.loan_id == loan_portfolio3.loan_id)\
    #     .filter(loan_portfolio3.loan_id==Loan_Portfolio.loan_id)\
    #     .filter(loan_portfolio3.status==1).scalar_subquery()
    main_user_case = case([(ProblemsCase.main_responsible_id == user.id, second_user.full_name)], else_=None).label("full_name")
    problems_case = db_session.query(ProblemsCase.id,
                                    LoanCase.id.label("loan_case_id"),
                                    LoanCase.monitoring_case_id.label("monitoring_case_id"),
                                    ProblemsCaseStatus.id.label('problem_status_id'),
                                    ProblemsCaseStatus.name.label('problem_status_name'),
                                    ProblemStates.name.label('state_chain_name'),
                                    ProblemStates.id.label('state_chain_id'),
                                    main_user_case,
                                    ProblemsCase.main_responsible_id,
                                    ProblemsCase.second_responsible_id,
                                    overdue_max_date_case,
                                    Loan_Portfolio.id.label('loan_portfolio_id'),
                                    Loan_Portfolio.loan_id,
                                    Loan_Portfolio.client_name,
                                    Loan_Portfolio.total_overdue,
                                    all_duty,
                                    Loan_Portfolio.overdue_balance,
                                    Loan_Portfolio.overdue_start_date,
                                    Loan_Portfolio.balance_16377,
                                    Loan_Portfolio.date_overdue_percent,
                                    sub_query_schedule_sum.label('total_overdue_by_graph'),
                                    client_region.name.label('region'),
                                    local_code.code.label('local_code'),
                                    currency.code.label('currency_code'),
                                    TaskManager.general_task_id,
                                    ProblemsCase.created_at,
                                    ProblemsCase.checked_status
                            )\
                .join(Loan_Portfolio, ProblemsCase.loan_portfolio_id == Loan_Portfolio.id, isouter=False)\
                .join(LoanCase, LoanCase.loan_portfolio_id == ProblemsCase.loan_portfolio_id)\
                .join(TaskManager, ProblemsCase.task_manager_id == TaskManager.id, isouter=True)\
                .join(ProblemsCaseStatus, ProblemsCase.problems_case_status_id == ProblemsCaseStatus.id, isouter=True)\
                .join(main_user, ProblemsCase.main_responsible_id == main_user.id, isouter=True)\
                .join(second_user, ProblemsCase.second_responsible_id == second_user.id, isouter=True)\
                .join(client_region, Loan_Portfolio.client_region == client_region.id, isouter=True)\
                .join(local_code, Loan_Portfolio.local_code_id == local_code.id, isouter=True)\
                .join(currency, Loan_Portfolio.currency_id == currency.id, isouter=True)\
                .join(ProblemStateChain, ProblemStateChain.loan_id == Loan_Portfolio.loan_id, isouter = True)\
                .join(ProblemStates, ProblemStates.id == ProblemStateChain.last_state_id, isouter = True)\
                .filter(Loan_Portfolio.status == 1)\
                .filter(Loan_Portfolio.is_taken_problem == True)\
                .filter(Loan_Portfolio.is_taken_non_target == False)\
                .filter(Loan_Portfolio.is_taken_out_of_balance == False)\
                .filter(all_duty!=None).filter(all_duty!=0)\
                # .filter(or_(and_(sub_query_schedule_date<datetime.now(), LoanPortfolioSchedule.date_red==sub_query_schedule_date), \
                #         and_(extract('month', LoanPortfolioSchedule.date_red) == period.month, \
                #             extract('year', LoanPortfolioSchedule.date_red) == period.year)))\
                #             .order_by(ProblemsCase.updated_at.desc())
                        
    
    if 'superviser' in user_roles:
        local_code_id = user.local_code
        
    if 'problem_block_filial_user' in user_roles:
        problems_case = problems_case.filter(ProblemsCase.second_responsible_id == user.id)
    
    if 'problem_block_filial_admin' in user_roles:
        problems_case = problems_case.filter(ProblemsCase.second_responsible_id == user.id)
        
    if 'problem_block_main_admin' in user_roles:
        problems_case = problems_case.filter(ProblemsCase.main_responsible_id == user.id)
            
            
    if main_responsible is not None:
        if 'main_superviser' in user_roles or 'main_superviser_problem' in user_roles:
            problems_case = problems_case.filter(ProblemsCase.main_responsible_id == main_responsible)
                
    
    if state_chain is not None:
        if state_chain == 4:
            problems_case = problems_case.join(JudicialData, ProblemsCase.id == JudicialData.problems_case_id, isouter = True)
            if task_status is not None:
                problems_case = problems_case.filter(JudicialData.judicial_status_id == task_status)
                
        if state_chain == 6:
            problems_case = problems_case.join(ProblemsAssets, ProblemsCase.id == ProblemsAssets.problems_case_id, isouter = True)
            if task_status is not None:
                problems_case = problems_case.filter(ProblemsAssets.assets_status_id == task_status)
                
        if state_chain == 7:
            problems_case = problems_case.join(OutOfBalance, ProblemsCase.id == OutOfBalance.problems_case_id, isouter = True)
            if task_status is not None:
                problems_case = problems_case.filter(OutOfBalance.out_of_balance_status_id == task_status)
                
                
        if state_chain == 8:
            problems_case = problems_case.join(ProblemsAuction, ProblemsCase.id == ProblemsAuction.problems_case_id, isouter = True)
            if task_status is not None:
                problems_case = problems_case.filter(ProblemsAuction.auction_status_id == task_status)
                
                
        if state_chain == 9:
            problems_case = problems_case.join(ProblemsMib, ProblemsCase.id == ProblemsMib.problems_case_id, isouter = True)
            if task_status is not None:
                problems_case = problems_case.filter(ProblemsMib.mib_ended_status_id == task_status)
     
    if region_id is not None:
        problems_case = problems_case.filter(Loan_Portfolio.client_region == region_id)
    
    if local_code_id is not None:
        problems_case = problems_case.filter(Loan_Portfolio.local_code_id == local_code_id)
    
    if loan_id is not None or client_name is not None:
        problems_case = problems_case.filter(or_(cast(Loan_Portfolio.loan_id, sqlalchemy.Text).like(f'{loan_id}%'), Loan_Portfolio.client_name.ilike(f'%{client_name}%')))
    
    if second_responsible is not None:
        problems_case = problems_case.filter(ProblemsCase.second_responsible_id == second_responsible)
    
    if is_target is not None:
        problems_case = problems_case.filter(loan_product.name == Loan_Portfolio.loan_product)\
        .filter(loan_product.is_target == is_target)
    
    if product_type is not None:
        problems_case = problems_case.filter(loan_product.name == Loan_Portfolio.loan_product)\
        .filter(loan_product.type == product_type) 
    
    
    if state_chain is not None:
        problems_case = problems_case.filter(ProblemStates.id == state_chain)
    
    
    if currency_id is not None:
        problems_case = problems_case.filter(Loan_Portfolio.currency_id == currency_id)
    
    if client_type is not None:    
        if client_type != '11' and client_type != '08':
            problems_case = problems_case.filter(Loan_Portfolio.borrower_type.regexp_match('^(?!08|11).*'))
        else:
            problems_case = problems_case.filter(Loan_Portfolio.borrower_type.regexp_match(f'^({client_type}).*'))
    
    if client_code is not None:
        problems_case = problems_case.filter(Loan_Portfolio.loan_account.regexp_match('\d{9}' + str(client_code) + '\d*' + '\d{3}'))
        
    problems_case = problems_case.order_by(ProblemsCase.updated_at.desc())        
    count = problems_case.count()
    problems_case = problems_case.limit(size).offset((page-1)*size).all()
    
    problems_case_list = []
    
    for problem in problems_case: 
        
        
        get_schedules = db_session.execute(text(f'''
                                               select * from loan_portfolio_schedule where loan_id = {problem.loan_id} order by date_red
                                               ''')).fetchall()
        
        if get_schedules[0].date_red > datetime.now():
            repayment_date = None
            recommended_amount = None
        elif get_schedules[-1].date_red < datetime.now():
            repayment_date = None
            recommended_amount = None
        else:
            for schedule in get_schedules:
                if period.year == schedule.date_red.year and period.month == schedule.date_red.month:
                    repayment_date = schedule.date_red
                    recommended_amount = schedule.summ_red
        
        
         
        get_problems_notifications = db_session.execute(text(f'''
                                               select id  from monitoring_notification where split_part(url, ':', 1)='{problem.loan_portfolio_id}'
                                               and to_user_id={user.id}
                                               and notification_type_id=4
                                               and is_read=false 
                                               ''')).fetchall()
        notifications = [notif.id for notif in get_problems_notifications]
        
        
        state_chain_status = get_state_chain_status(problem.state_chain_id, problem.id, db_session)
        
        
        
        #problems_monitoring = get_problems_monitoring(problem, db_session)
        
        
        
        if problem.overdue_max_date is not None:
            overdue_days = (datetime.now().date() - problem.overdue_max_date).days
        
        
        recommended_amount = recommended_amount and float(recommended_amount)/100 or None
        loan_client = problem.loan_id
        if problem.client_name is not None:
            loan_client = str(problem.loan_id) +' : '+ problem.client_name
        total_overdue = 0
        total_overdue_by_graph = 0
        if problem.total_overdue is not None and  problem.total_overdue !='0':
            total_overdue = problem.total_overdue
        if problem.total_overdue_by_graph is not None and problem.total_overdue_by_graph!=0:
            total_overdue_by_graph = problem.total_overdue_by_graph/100
        if float(total_overdue) < total_overdue_by_graph:
            recommended_amount = 0
        if (problem.all_duty == 0 or problem.all_duty is None) and recommended_amount == 0:
            continue
        if repayment_date is None or repayment_date<(datetime.now()-timedelta(30)):
            recommended_amount = None
        
        problems_case_list.append({"id":problem.id,
                                  "loan_case_id":problem.loan_case_id,
                                  "monitoring_case_id":problem.monitoring_case_id,
                                  'state_chain_name':problem.state_chain_name,
                                  'state_chain_status':state_chain_status,
                               "loan_portfolio": {"id":problem.loan_portfolio_id,
                                                  "region": problem.region,
                                                  "local_code": problem.local_code,
                                                  "total_overdue": problem.total_overdue,
                                                  "loan_client":loan_client,
                                                  "loan_id":problem.loan_id,
                                                  "client_name":problem.client_name,
                                                  "all_duty": problem.all_duty,
                                                  "overdue_balance": problem.overdue_balance,
                                                  "overdue_max_date": problem.overdue_max_date,
                                                  "overdue_days":overdue_days,
                                                  "overdue_start_date": problem.overdue_start_date,
                                                  "balance_16377": problem.balance_16377,
                                                  "date_overdue_percent": problem.date_overdue_percent,
                                                  "total_overdue_by_graph": problem.total_overdue_by_graph
                                                  },
                               "loan_portfolio_schedule": {
                                   "repayment_date": repayment_date,
                                   "recommended_amount":recommended_amount,
                                   "currency_code":problem.currency_code
                               },
                               "responsible": {"full_name":problem.full_name},
                               "main_responsible": problem.main_responsible_id,
                               "second_responsible": problem.second_responsible_id,
                               "general_task":problem.general_task_id,
                               "case_status": {"id": problem.problem_status_id,
                                               "name": problem.problem_status_name},
                               "kad_letter_35":KGT.SEND_1_LETTER.value,
                               "kad_letter_45":KGT.SEND_2_LETTER.value,
                               "created_at":problem.created_at,
                               "checked_status":problem.checked_status,
                               "count":notifications})
    
    return {"items": problems_case_list,
            "total":count,
            "page":page,
            "size":size} 





def get_problems_monitoring(case, db_session):
    deadline = None
    task_status = None
    main_responsible_due_date = None
    main_responsible_expired = None
    second_responsible_due_date = None
    second_responsible_expired = None
    expired = False
    get_problems_monitoring = get_last_problem_monitoring(case.id, db_session)
    if get_problems_monitoring is not None:
        if get_problems_monitoring.main_responsible_due_date is not None:
            main_responsible_due_date = get_problems_monitoring.main_responsible_due_date
            if (main_responsible_due_date - get_problems_monitoring.second_responsible_due_date).days > 2:
                main_responsible_expired = (main_responsible_due_date - get_problems_monitoring.second_responsible_due_date).days -2
            
        if get_problems_monitoring.second_responsible_due_date is not None:
            second_responsible_due_date = get_problems_monitoring.second_responsible_due_date
            if (get_problems_monitoring.second_responsible_due_date.date() - get_problems_monitoring.deadline).days > 0:
                second_responsible_expired = (second_responsible_due_date.date() - get_problems_monitoring.deadline).days
        
        deadline = get_problems_monitoring.deadline
        task_status = get_problems_monitoring.status.name
        if get_problems_monitoring.status.id !=  monitoring_status["проверено"]:
            if get_problems_monitoring.deadline < datetime.now().date():
                expired = True
            
        return make_object(deadline, task_status, main_responsible_due_date, main_responsible_expired,
                                    second_responsible_due_date, second_responsible_expired, expired, "Проблемный мониторинг")
    else:
        return None



    

def get_state_chain_status(state_id, problem_case_id, db_session):
    
    '''
    1	"Почта 35"
    2	"Почта 45"
    3	"ССП"
    4	"СУД"
    5	"МИБ"
    6	"Пробл. Акт"
    7	"Вне баланс"
    8	"Аукцион"
    9	"Прекращено в БПИ"
    '''
    get_status=None
    if state_id == 4:
        get_status = db_session.execute(text(f'''
                                               select 
                                               pas.name 
                                               from judicial_data jd 
                                               join problems_assets_status pas on pas.id=jd.judicial_status_id
                                               where jd.problems_case_id={problem_case_id} order by jd.id desc
                                               ''')).fetchone()
        get_status = get_status and get_status[0]

    if state_id == 6:
        get_status = db_session.execute(text(f'''
                                               select 
                                               pas.name 
                                               from problems_assets pa 
                                               join problems_assets_status pas on pas.id=pa.assets_status_id
                                               where pa.problems_case_id={problem_case_id} order by pa.id desc
                                               ''')).fetchone()
        get_status = get_status and get_status[0]
    
    if state_id == 7:
        get_status = db_session.execute(text(f'''
                                               select 
                                               pas.name 
                                               from out_of_balance ob 
                                               join problems_assets_status pas on pas.id=ob.out_of_balance_status_id
                                               where ob.problems_case_id={problem_case_id} order by ob.id desc
                                               ''')).fetchone()
        get_status = get_status and get_status[0]
    
    
    if state_id == 8:
        get_status = db_session.execute(text(f'''
                                               select 
                                               pas.name 
                                               from problems_auction pa 
                                               join problems_assets_status pas on pas.id=pa.auction_status_id
                                               where pa.problems_case_id={problem_case_id} order by pa.id desc
                                               ''')).fetchone()
        get_status = get_status and get_status[0]
        
    if state_id == 9:
        get_status = db_session.execute(text(f'''
                                               select 
                                               pas.name 
                                               from problems_mib pm 
                                               join problems_assets_status pas on pas.id=pm.mib_ended_status_id
                                               where pm.problems_case_id={problem_case_id} order by pm.id desc
                                               ''')).fetchone()    
        get_status = get_status and get_status[0]
    
    return get_status
    
def make_object(deadline, task_status, main_responsible_due_date, main_responsible_expired,
                second_responsible_due_date, second_responsible_expired, expired, general_task):
    return {"deadline": deadline,
                    "task_status":task_status,
                    "main_responsible_due_date": main_responsible_due_date,
                    "main_responsible_expired": main_responsible_expired,
                    "second_responsible_due_date": second_responsible_due_date,
                    "second_responsible_expired": second_responsible_expired,
                    "expired": expired,
                    "general_task":general_task}




def get_last_problem_monitoring(problems_case_id, db_session):
    get_problems_monitoring  = db_session.query(ProblemsMonitoring).filter(ProblemsMonitoring.problems_case_id == problems_case_id).order_by(ProblemsMonitoring.id.desc()).first()
    
    if get_problems_monitoring is not None:
        return get_problems_monitoring
    return None




def get_promblems_data_for_main_page(db_session):
    
    data = db_session.query(func.count(Loan_Portfolio.id).label('loan_count'), \
                            func.sum(cast(Loan_Portfolio.total_overdue, sqlalchemy.FLOAT)).label('total_overdue'),\
                            func.sum(cast(Loan_Portfolio.overdue_balance, sqlalchemy.FLOAT)).label('overdue_balance'),\
                            func.sum(cast(Loan_Portfolio.balance_16377, sqlalchemy.FLOAT)).label('balance_16377'),\
                            (func.sum(cast(Loan_Portfolio.overdue_balance, sqlalchemy.FLOAT)) + func.sum(cast(Loan_Portfolio.balance_16377, sqlalchemy.FLOAT))).label('all_duty'))\
        .filter(Loan_Portfolio.status == 1).first()

    overdue_loan = db_session.query(func.count(Loan_Portfolio.id).label('overdue_loan_count'))\
        .filter(Loan_Portfolio.overdue_balance != None).filter(Loan_Portfolio.balance_16377 != None).filter(Loan_Portfolio.status == 1).first()

    return {"loan_count":data.loan_count,
            "total_overdue":data.total_overdue,
            "overdue_balance":data.overdue_balance,
            "balance_16377":data.balance_16377,
            "all_duty":data.all_duty,
            "overdue_loan_count":overdue_loan.overdue_loan_count}
    
    
    
    
    
    
    
    
    
def get_problems_case_details(problem_case_id, db_session):
    
    main_user = aliased(users_model)
    second_user = aliased(users_model)
    
    problems_case = db_session.query(ProblemsCase.id,
                                     ProblemStates.name.label('state_chain_name'),
                                     LoanCase.monitoring_case_id,
                                    ProblemsCase.main_responsible_id,
                                    ProblemsCase.second_responsible_id,
                                    Loan_Portfolio.id.label('loan_portfolio_id')
                            )\
                .join(Loan_Portfolio, ProblemsCase.loan_portfolio_id == Loan_Portfolio.id, isouter=False)\
                .join(main_user, ProblemsCase.main_responsible_id == main_user.id, isouter=True)\
                .join(second_user, ProblemsCase.second_responsible_id == second_user.id, isouter=True)\
                .join(LoanCase, LoanCase.loan_portfolio_id == ProblemsCase.loan_portfolio_id)\
                .join(ProblemStateChain, ProblemStateChain.loan_id == Loan_Portfolio.loan_id, isouter = True)\
                .join(ProblemStates, ProblemStates.id == ProblemStateChain.last_state_id, isouter = True)\
                    .filter(ProblemsCase.id == problem_case_id).first()
    
    problems_case_list = {}
    
    problems_case_list = {"id":problems_case.id,
                          "monitoring_case_id": problems_case.monitoring_case_id,
                          'state_chain_name':problems_case.state_chain_name,
                            "loan_portfolio": {"id":problems_case.loan_portfolio_id},
                            "kad_letter_35":KGT.SEND_1_LETTER.value,
                               "kad_letter_45":KGT.SEND_2_LETTER.value,
                               "main_responsible": problems_case.main_responsible_id,
                               "second_responsible": problems_case.second_responsible_id}
    
    return problems_case_list
            