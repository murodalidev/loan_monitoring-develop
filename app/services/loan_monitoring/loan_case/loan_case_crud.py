import datetime
from sqlalchemy import or_, and_
import sqlalchemy
from sqlalchemy.sql import text
from sqlalchemy.sql.expression import cast
from ....models.loan_case.loan_case_model import LoanCase
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ....models.monitoring_task_manager.general_tasks_model import GeneralTasks
from ....models.monitoring_task_manager.task_manager_model import TaskManager
from ....models.users.users import Users as users_model
from ..general_tasks import general_tasks_crud
from ..juridical_case import juridical_case_crud
from ....models.brief_case.directories.loan_product import loan_product
from ..task_manager.task_manager_crud import TaskManager_class
from ...users.users_crud import Users
from ...monitoring_files import files_crud
from ....common.commit import commit_object, flush_object
from ....common.is_empty import is_empty, is_empty_list, is_exists
from ....models.monitoring_case.monitoring_case_model import MonitoringCase
from ....models.problems_case.problems_case_model import ProblemsCase
from ....models.juridical_case.juridical_case_model import JuridicalCase
from ....models.monitoring_case.target_monitoring_model import TargetMonitoring
from ....models.monitoring_case.scheduled_monitoring_model import ScheduledMonitoring
from ....models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_model import UnscheduledMonitoring
from ....schemas.task_manager_schemas import UpdateTaskManagerSetResponsible, UpdateTaskManagerAccept
from  app.services.users.users_crud import Users as users
from ....models.loan_case.loan_case_history_model import LoanCaseHistory
from ....models.juridical_case.juridical_case_history_model import JuridicalCaseHistory
from ....schemas.notification_schemas import CreateNotification
from ..notification.notification_crud import Notificaton_class
from ....common.dictionaries import notification_dictionary
from fastapi.responses import FileResponse
from ....common.dictionaries.task_status_dictionaries import task_status
from ....models.files.monitoring_files_model import MonitoringFiles
from ....common.dictionaries.monitoring_case_dictionary import loan_case, problems_case, juridic_case
from ....common.dictionaries.case_history_dictionaries import loan_case_history, juridical_case_history, problem_case_history
from ..loan_case import loan_case_crud
from ..monitoring_case import monitoring_case_crud
from ....common.dictionaries.departments_dictionary import DEP, ROLES
from ....common.dictionaries.general_tasks_dictionary import JGT, MGT, PGT, GTCAT

def appoint_responsible(request, db_session):
    get_monitoring_case = db_session.query(LoanCase)\
        .filter(LoanCase.second_responsible_id == request.second_responsible_id)\
            .filter(LoanCase.id == request.loan_case_id).all()
    is_empty_list(get_monitoring_case, 400, 'Already appointed!')
    get_loan_case = loan_caseUpdate_second_responsible(request.loan_case_id, request.second_responsible_id, db_session)
    
    new_loan_case_history = LoanCaseHistory(loan_case_id = request.loan_case_id, 
                                            general_task_id = request.general_task_id,
                                            from_user_id = get_loan_case.main_responsible_id, 
                                            to_user_id= request.second_responsible_id,
                                            created_at = datetime.datetime.now(),
                                            message = loan_case_history['appoint_responsible']
                                                )
    db_session.add(new_loan_case_history)
    
    
    new_monitoring_case = MonitoringCase(monitoring_case_status_id = loan_case['Новый'],
                                         created_at = datetime.datetime.now())
    db_session.add(new_monitoring_case)
    flush_object(db_session)
    
    
    loan_case_crud.loan_caseUpdate_monitoring_case(request.loan_case_id, new_monitoring_case.id, db_session)
    flush_object(db_session)
    
    data = UpdateTaskManagerSetResponsible()
    data.task_manager_id = request.task_manager_id
    data.general_task_id = request.general_task_id
    data.task_status = task_status['впроцессе']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    
    
    data = CreateNotification()
    data.from_user_id = get_loan_case.main_responsible_id
    data.to_user_id = request.second_responsible_id
    data.notification_type = notification_dictionary.notification_type['monitoring']
    data.body = notification_dictionary.notification_body['appoint_responsible']
    data.url = f'{get_loan_case.loan_portfolio_id}'+':'+ f'{get_loan_case.id}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    commit_object(db_session)
    return {"OK"}
    
    
    
    
def appoint_responsiblev2(request, db_session):
    get_monitoring_case = db_session.query(LoanCase)\
        .filter(LoanCase.second_responsible_id == request.second_responsible_id)\
            .filter(LoanCase.id == request.loan_case_id).all()
    is_empty_list(get_monitoring_case, 400, 'Already appointed!')
    get_loan_case = loan_caseUpdate_second_responsible(request.loan_case_id, request.second_responsible_id, db_session)
    
    new_loan_case_history = LoanCaseHistory(loan_case_id = request.loan_case_id, 
                                            general_task_id = request.general_task_id,
                                            from_user_id = get_loan_case.main_responsible_id, 
                                            to_user_id= request.second_responsible_id,
                                            created_at = datetime.datetime.now(),
                                            message = loan_case_history['appoint_responsible']
                                                )
    db_session.add(new_loan_case_history)
    
    
    new_monitoring_case = MonitoringCase(monitoring_case_status_id = loan_case['Новый'],
                                         created_at = datetime.datetime.now())
    db_session.add(new_monitoring_case)
    flush_object(db_session)
    
    
    get_loan_case = loan_case_crud.loan_caseUpdate_monitoring_case(request.loan_case_id, new_monitoring_case.id, db_session)
    flush_object(db_session)
    
    data = UpdateTaskManagerSetResponsible()
    data.task_manager_id = get_loan_case.task_manager_id
    data.general_task_id = request.general_task_id
    data.task_status_id = task_status['впроцессе']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    
    
    data = CreateNotification()
    data.from_user_id = get_loan_case.main_responsible_id
    data.to_user_id = request.second_responsible_id
    data.notification_type = notification_dictionary.notification_type['monitoring'] 
    data.body = notification_dictionary.notification_body['appoint_responsible']
    data.url = f'{get_loan_case.loan_portfolio_id}'+':'+ f'{get_loan_case.id}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    commit_object(db_session)
    return {"OK"}
    
    
def update_responsible(request, db_session):
    for loan_case_id in request.accept:#TODO notification
        loan_caseUpdate_second_responsible(loan_case_id, request.second_responsible_id, db_session)
        flush_object(db_session)
    commit_object(db_session)
    return {"OK"}
    
def appoint_responsible_list_tasks(loan_case_obj, db_session):
    new_monitoring_case = MonitoringCase(monitoring_case_status_id = loan_case['Новый'],
                                         created_at = datetime.datetime.now())
    db_session.add(new_monitoring_case)
    flush_object(db_session)
    
    loan_case_obj.monitoring_case_id = new_monitoring_case.id
    loan_case_obj.updated_at = datetime.datetime.now()
    flush_object(db_session)
    
    return new_monitoring_case
    




# def get_all_loan_case(size, page, region_id, local_code_id, loan_id, client_name, is_target, product_type, client_type, task_status_id, client_code, expired, start_period, end_period, user_id, department, db_session):
#     loan_case_list = []
#     if department == DEP.PROBLEM.value:
#         case = db_session.query(ProblemsCase)\
#             .filter(or_(ProblemsCase.main_responsible_id == user_id, ProblemsCase.second_responsible_id == user_id))\
#                 .filter(ProblemsCase.problems_case_status_id != problems_case['закрыт'])
                
#         if loan_id is not None or client_name is not None:
#             case = case.filter(ProblemsCase.loan_portfolio_id == Loan_Portfolio.id).filter(or_(cast(Loan_Portfolio.loan_id, sqlalchemy.Text).like(f'{loan_id}%'), Loan_Portfolio.client_name.ilike(f'%{client_name}%')))
        
#         if is_target is not None:
#             case = case.filter(ProblemsCase.loan_portfolio_id == Loan_Portfolio.id).filter(loan_product.name == Loan_Portfolio.loan_product)\
#             .filter(loan_product.is_target == is_target)
        
#         if client_type != '11' and client_type != '08':
#             case = case.filter(ProblemsCase.loan_portfolio_id == Loan_Portfolio.id).filter(Loan_Portfolio.borrower_type.regexp_match('^(?!08|11).*'))
#         else:
#             case = case.filter(ProblemsCase.loan_portfolio_id == Loan_Portfolio.id).filter(Loan_Portfolio.borrower_type.regexp_match(f'^({client_type}).*'))
#         case = case.order_by(ProblemsCase.id.asc())
        
        
#     elif department == DEP.JURIDIC.value:
#         case = db_session.query(JuridicalCase)\
#             .filter(or_(JuridicalCase.main_responsible_id == user_id, JuridicalCase.second_responsible_id == user_id))\
#                 .filter(JuridicalCase.juridical_case_status_id !=juridic_case['закрыт'])
        
#         if loan_id is not None or client_name is not None:
#             case = case.filter(JuridicalCase.loan_portfolio_id == Loan_Portfolio.id).filter(or_(cast(Loan_Portfolio.loan_id, sqlalchemy.Text).like(f'{loan_id}%'), Loan_Portfolio.client_name.like(f'%{client_name}%')))
        
#         if is_target is not None:
#             case = case.filter(JuridicalCase.loan_portfolio_id == Loan_Portfolio.id).filter(loan_product.name == Loan_Portfolio.loan_product)\
#             .filter(loan_product.is_target == is_target)
            
#         if product_type is not None:
#             case = case.filter(JuridicalCase.loan_portfolio_id == Loan_Portfolio.id).filter(loan_product.name == Loan_Portfolio.loan_product)\
#             .filter(loan_product.type == product_type)        
    
#         if client_type is not None:
#             if client_type != '11' and client_type != '08':
#                 case = case.filter(JuridicalCase.loan_portfolio_id == Loan_Portfolio.id).filter(Loan_Portfolio.borrower_type.regexp_match('^(?!08|11).*'))
#             else:
#                 case = case.filter(JuridicalCase.loan_portfolio_id == Loan_Portfolio.id).filter(Loan_Portfolio.borrower_type.regexp_match(f'^({client_type}).*'))
        
#         case = case.order_by(JuridicalCase.id.asc())
        
#     else:
#         case = db_session.query(LoanCase).filter(or_(LoanCase.main_responsible_id == user_id, LoanCase.second_responsible_id == user_id))
        
#         if region_id is not None:
#             case = case.filter(LoanCase.loan_portfolio_id == Loan_Portfolio.id).filter(Loan_Portfolio.client_region == region_id)
        
#         if local_code_id is not None:
#             case = case.filter(LoanCase.loan_portfolio_id == Loan_Portfolio.id).filter(Loan_Portfolio.local_code_id == local_code_id)
        
#         if loan_id is not None or client_name is not None:
#             case = case.filter(LoanCase.loan_portfolio_id == Loan_Portfolio.id).filter(or_(cast(Loan_Portfolio.loan_id, sqlalchemy.Text).like(f'{loan_id}%'), Loan_Portfolio.client_name.ilike(f'%{client_name}%')))
        
        
#         if is_target is not None:
#             case = case.filter(LoanCase.loan_portfolio_id == Loan_Portfolio.id).filter(loan_product.name == Loan_Portfolio.loan_product)\
#             .filter(loan_product.is_target == is_target)
        
#         if product_type is not None:
#             case = case.filter(LoanCase.loan_portfolio_id == Loan_Portfolio.id).filter(loan_product.name == Loan_Portfolio.loan_product)\
#             .filter(loan_product.type == product_type) 
        
#         if client_type is not None:    
#             if client_type != '11' and client_type != '08':
#                 case = case.filter(LoanCase.loan_portfolio_id == Loan_Portfolio.id).filter(Loan_Portfolio.borrower_type.regexp_match('^(?!08|11).*'))
#             else:
#                 case = case.filter(LoanCase.loan_portfolio_id == Loan_Portfolio.id).filter(Loan_Portfolio.borrower_type.regexp_match(f'^({client_type}).*'))
        
#         if task_status_id is not None:
#             case = case.filter(LoanCase.task_manager_id == TaskManager.id).filter(TaskManager.general_task_id == task_status_id)
#         if client_code is not None:
#             case = case.filter(LoanCase.loan_portfolio_id == Loan_Portfolio.id).filter(Loan_Portfolio.loan_account.regexp_match('\d{9}' + str(client_code) + '\d*' + '\d{3}'))
#         if expired:
#             case = case.filter(MonitoringCase.id == LoanCase.monitoring_case_id).filter(LoanCase.monitoring_case_id != None)\
#                     .filter(MonitoringCase.target_monitoring_id == TargetMonitoring.id).filter(MonitoringCase.target_monitoring_id != None)\
#                     .filter(TargetMonitoring.target_monitoring_result_id == None)\
#                     .filter(TargetMonitoring.deadline < datetime.datetime.now().date())\
            
#             case1 = db_session.query(LoanCase).filter(or_(LoanCase.main_responsible_id == user_id, LoanCase.second_responsible_id == user_id))\
#                 .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
#                 .filter(MonitoringCase.id == ScheduledMonitoring.monitoring_case_id)\
#                 .filter(ScheduledMonitoring.task_manager_id == TaskManager.id)\
#                 .filter(ScheduledMonitoring.deadline < datetime.datetime.now().date())
#             case = case.union(case1)
        
#         # start_period = '2023-25-08'
#         # end_period = '2023-27-08'
        
#         if start_period is not None and end_period is not None:
#             start_period = datetime.datetime.strptime(start_period, '%Y-%m-%d').date()
#             end_period = datetime.datetime.strptime(end_period, '%Y-%m-%d').date()
#             case = case.filter(MonitoringCase.id == LoanCase.monitoring_case_id).filter(LoanCase.monitoring_case_id != None)\
#                 .filter(MonitoringCase.target_monitoring_id == TargetMonitoring.id).filter(MonitoringCase.target_monitoring_id != None)\
#                 .filter(TargetMonitoring.target_monitoring_result_id == None)\
#                 .filter(and_(TargetMonitoring.deadline >= start_period, TargetMonitoring.deadline <= end_period))
            
#             case1 = db_session.query(LoanCase).filter(or_(LoanCase.main_responsible_id == user_id, LoanCase.second_responsible_id == user_id))\
#                 .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
#                 .filter(MonitoringCase.id == ScheduledMonitoring.monitoring_case_id)\
#                 .filter(ScheduledMonitoring.task_manager_id == TaskManager.id)\
#                 .filter(and_(ScheduledMonitoring.deadline <= start_period, ScheduledMonitoring.deadline >= end_period))
#             case2 = db_session.query(LoanCase).filter(or_(LoanCase.main_responsible_id == user_id, LoanCase.second_responsible_id == user_id))\
#                 .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
#                 .filter(MonitoringCase.id == UnscheduledMonitoring.monitoring_case_id)\
#                 .filter(UnscheduledMonitoring.task_manager_id == TaskManager.id)\
#                 .filter(and_(UnscheduledMonitoring.deadline <= start_period, UnscheduledMonitoring.deadline >= end_period))
#             case = case.union(case1).union(case2)
            
            
#         case = case.order_by(LoanCase.updated_at.desc())
      
        
#     count = case.count()
#     case = case.limit(size).offset((page-1)*size).all()
    
    
#     for loan in case:
#         tasks = TaskManager_class.get_task_manager_by_id(loan.task, db_session)
#         if loan.main_responsible.department == DEP.PROBLEM.value:
#             case_status = loan.problems_case_status_id and loan.status or None
#         elif loan.main_responsible.department == DEP.JURIDIC.value:
#             case_status = loan.juridical_case_status_id and loan.status or None
#         else: case_status = loan.loan_case_status_id and loan.status or None
#         loan_client = loan.portfolio.loan_id
#         if loan.portfolio.client_name is not None:
#             loan_client = str(loan_client) +' : '+ loan.portfolio.client_name
#         deadline = []
#         if loan.main_responsible.department == DEP.KAD.value:   
            
#             deadline = monitoring_case_crud.get_target_monitoring_deadline(loan, db_session)
#             if deadline["deadline"] is None:
#                 deadline = monitoring_case_crud.get_plan_monitoring_deadline(loan, db_session)
        
#         loan_case_list.append({"id":loan.id,
#                                "loan_portfolio": {"id":loan.portfolio.id,
#                                                   "region": loan.portfolio.client_region and loan.portfolio.region or None,
#                                                   "local_code": loan.portfolio.local_code_id and loan.portfolio.local_code.code or None,
#                                                   "total_overdue": loan.portfolio.total_overdue,
#                                                   "loan_client":loan_client,
#                                                   "loan_id":loan.portfolio.loan_id,
#                                                   "client_name":loan.portfolio.client_name,},
#                                "main_responsible":{"id":loan.main_responsible and loan.main_responsible.id,
#                                           "full_name":loan.main_responsible and loan.main_responsible.full_name,
#                                           "bank_mfo":{"id":loan.main_responsible and loan.main_responsible.branch.id,
#                                                         "bank_mfo":loan.main_responsible and loan.main_responsible.branch.code,
#                                                         "name":loan.main_responsible and loan.main_responsible.branch.name}},
#                                "second_responsible":{"id":loan.second_responsible and loan.second_responsible.id,
#                                           "full_name":loan.second_responsible and loan.second_responsible.full_name,
#                                           "bank_mfo":{"id":loan.second_responsible and loan.second_responsible.branch.id,
#                                                         "bank_mfo":loan.second_responsible and loan.second_responsible.branch.code,
#                                                         "name":loan.second_responsible and loan.second_responsible.branch.name}},
#                                "general_task":tasks['general_task'],
#                                "case_status": case_status,
#                                 "expired":deadline and (deadline['expired'] and deadline['expired']),
#                                 "deadline":deadline and (deadline['deadline'] and deadline['deadline']),
#                                "created_at":loan.created_at})
#     return {"items": loan_case_list,
#             "total":count,
#             "page":page,
#             "size":size} 
    
    
    
    
    
def get_loan_case_details(id, db_session):
    loan_case = {}
    unscheduled = False
    scheduled = False
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == id).first()
    get_scheduled = db_session.query(ScheduledMonitoring).filter(ScheduledMonitoring.monitoring_case_id == get_loan_case.monitoring_case_id).all()
    if get_scheduled != []:
        scheduled = True
    get_unscheduled = db_session.query(UnscheduledMonitoring).filter(UnscheduledMonitoring.monitoring_case_id == get_loan_case.monitoring_case_id)\
            .filter(UnscheduledMonitoring.second_responsible_due_date == None).all()
    if get_unscheduled != []:
        unscheduled = True
    
    if get_loan_case is not None:
        loan_case ={"id":get_loan_case.id,
                      "loan_portfolio":{"id":get_loan_case.portfolio.id,
                                        "issue_date":get_loan_case.portfolio.issue_date,
                                        "local_code":{ "id":get_loan_case.portfolio.local_code.id,
                                                        "code":get_loan_case.portfolio.local_code.code,
                                                        "name":get_loan_case.portfolio.local_code.name}},
                            "main_responsible":{"id":get_loan_case.main_responsible_id and get_loan_case.main_responsible.id,
                                          "full_name":get_loan_case.main_responsible_id and get_loan_case.main_responsible.full_name,
                                          "local_code":{"id":get_loan_case.main_responsible_id and get_loan_case.main_responsible.local.id,
                                                        "code":get_loan_case.main_responsible_id and get_loan_case.main_responsible.local.code,
                                                        "name":get_loan_case.main_responsible_id and get_loan_case.main_responsible.local.name}},
                            "second_responsible":{"id":get_loan_case.second_responsible and get_loan_case.second_responsible.id,
                                          "full_name":get_loan_case.second_responsible and get_loan_case.second_responsible.full_name,
                                          "local_code":{"id":get_loan_case.main_responsible_id and get_loan_case.second_responsible.local.id,
                                                        "code":get_loan_case.main_responsible_id and get_loan_case.second_responsible.local.code,
                                                        "name":get_loan_case.main_responsible_id and get_loan_case.second_responsible.local.name}},
                            "unschedule": unscheduled,
                            "schedule": scheduled,
                            "monitoring_case":get_loan_case.monitoring_case_id and get_loan_case.monitoring_case_id or None,
                            "loan_case_status":get_loan_case.loan_case_status_id and get_loan_case.status.name or None,
                            "target_deadline_extension_status":get_loan_case.target_deadline_extension_status_id and get_loan_case.target_deadline_extension_status or None,
                            "scheduled_deadline_extension_status":get_loan_case.scheduled_deadline_extension_status_id and get_loan_case.scheduled_deadline_extension_status or None,
                            "unscheduled_deadline_extension_status":get_loan_case.unscheduled_deadline_extension_status_id and get_loan_case.unscheduled_deadline_extension_status or None,
                            
                            "created_at":get_loan_case.created_at and get_loan_case.created_at or None,
                            "updated_at":get_loan_case.updated_at and get_loan_case.updated_at or None}
        tasks = TaskManager_class.get_task_manager_by_id(get_loan_case.task, db_session)
        gerenal_tasks_list = general_tasks_crud.get_general_tasks_by_category_id(get_loan_case.task.general_task.category.id, db_session)
        
        return {"loan_case":loan_case,
                "task":tasks,
                "general_tasks":gerenal_tasks_list,
                }
    
    
    
    
    
def create_loan_case_with_append_task(task, data, db_session):#used
    new_loan_case = LoanCase(loan_portfolio_id = data.loan_portfolio_id,
                                 main_responsible_id = data.main_responsible_id,
                                 target_deadline_extension_status_id = 1,
                                 scheduled_deadline_extension_status_id = 1,
                                 unscheduled_deadline_extension_status_id = 1,
                                 second_responsible_id = data.second_responsible_id,
                                 loan_case_status_id = loan_case['Новый'],
                                 task_manager_id = task.id,
                                 created_at = datetime.datetime.now()
                                 )
    db_session.add(new_loan_case)
    flush_object(db_session)
    return new_loan_case
    
    
def check_if_loan_case_empty(accept, db_session):#used
    portfolios = []
    for portfolio in accept:
        portfolios.append(portfolio.loan_portfolio_id)
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.loan_portfolio_id.in_(portfolios and portfolios or ())).all()
    is_empty_list(get_loan_case, 400,'Loans have already taken.')
    
  
    
    
def loan_caseUpdate_monitoring_case(loan_case_id, monitoring_case_id, db_session):#used
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == loan_case_id).first()
    
    get_loan_case.monitoring_case_id = monitoring_case_id
    get_loan_case.updated_at = datetime.datetime.now()
    return get_loan_case


def loan_caseUpdate_second_responsible(loan_case_id, second_responsible_id, db_session):#used
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == loan_case_id).first()
    
    new_loan_case_history = LoanCaseHistory(loan_case_id = loan_case_id, 
                                            general_task_id = get_loan_case.task.general_task_id,
                                            from_user_id = get_loan_case.main_responsible_id, 
                                            to_user_id= get_loan_case.second_responsible_id,
                                            created_at = datetime.datetime.now(),
                                            message = loan_case_history['change_responsible']
                                                )
    db_session.add(new_loan_case_history)
    
    
    
    get_loan_case.second_responsible_id = second_responsible_id
    get_loan_case.updated_at = datetime.datetime.now()
    return get_loan_case


def loan_caseChange_second_responsible(loan_case_id, second_responsible_id, db_session):#used
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == loan_case_id).first()
    
    get_loan_case.second_responsible_id = second_responsible_id
    get_loan_case.updated_at = datetime.datetime.now()
    return get_loan_case



def loan_caseUpdate_close(loan_case_id, db_session):
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == loan_case_id).first()
    
    get_loan_case.loan_case_status_id = loan_case['закрыт']
    get_loan_case.updated_at = datetime.datetime.now()
    return get_loan_case

def loan_caseUpdate_problems_case(loan_case_id, problems_case_id, db_session):
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == loan_case_id).first()
    
    get_loan_case.problems_case_id = problems_case_id
    get_loan_case.updated_at = datetime.datetime.now()




def update_loan_case_set_status_closed(loan_case_id, db_session):
    prob_case = db_session.query(LoanCase).filter(LoanCase.id ==loan_case_id).first()
    prob_case.loan_case_status_id = loan_case['закрыт']
    prob_case.updated_at = datetime.datetime.now()
    flush_object(db_session)
    return prob_case


def update_loan_case_set_status_waiting(loan_case_id, db_session):
    prob_case = db_session.query(LoanCase).filter(LoanCase.id ==loan_case_id).first()
    prob_case.loan_case_status_id = loan_case['ожидание']
    prob_case.updated_at = datetime.datetime.now()
    flush_object(db_session)
    return prob_case


def get_loan_case_history(loan_case_id,general_task_id, db_session):
    case_history = []
    
    loan_case_history = db_session.query(LoanCaseHistory).filter(LoanCaseHistory.general_task_id == general_task_id)\
        .filter(LoanCaseHistory.loan_case_id == loan_case_id).order_by(LoanCaseHistory.created_at.asc()).all()
    
    
    for history in loan_case_history:
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
                             'files': history.files and files_crud.get_case_files(history)})
        
    return case_history



def get_file(file_path):
    filename = file_path.replace('project_files/monitoring_files/','')
    return FileResponse(file_path, filename=filename)



def close_loan_case(request, db_session):
    get_loan_case = db_session.query(LoanCase)\
        .filter(LoanCase.id == request.loan_case_id)\
            .filter(LoanCase.loan_case_status_id != loan_case['закрыт']).first()
    is_exists(get_loan_case, 400, 'Already closed!')
    
    get_loan_case.loan_case_status_id = loan_case['закрыт']
    get_loan_case.updated_at = datetime.datetime.now()
    get_loan_case.monitoring_case.monitoring_case_status_id = loan_case['закрыт']
    get_loan_case.portfolio.status = 3
    
    new_loan_case_history = LoanCaseHistory(loan_case_id = request.loan_case_id, 
                                            general_task_id = request.general_task_id,
                                            from_user_id = get_loan_case.main_responsible_id, 
                                            created_at = datetime.datetime.now(),
                                            message = loan_case_history['close']
                                                )
    db_session.add(new_loan_case_history)
    
    data = UpdateTaskManagerSetResponsible()
    data.task_manager_id = request.task_manager_id
    data.general_task_id = request.general_task_id
    
    task = TaskManager_class(data)
    task.update_task_manager_problems_set_closed(db_session)
    #TODO: close problems and juridic if exists
    
    commit_object(db_session)
    return {"OK"}





def reply_to_new_juridical_case(request, file_path, db_session):
    juridical_case = db_session.query(JuridicalCase).filter(JuridicalCase.loan_portfolio_id == request.loan_portfolio_id)\
        .filter(JuridicalCase.juridical_case_status_id == juridic_case['новый']).first()
        
    data = UpdateTaskManagerAccept()
    data.task_manager_id = juridical_case.task_manager_id
    data.task_status = task_status['на проверку']
    task = TaskManager_class(data)
    juridic_task = task.update_task_manager(db_session)
    
    new_juridical_case_history = JuridicalCaseHistory(juridical_case_id = juridical_case.id, 
                                                general_task_id = JGT.COORDINATE_DOCUMENTS.value,
                                                from_user_id = request.from_user, 
                                                created_at = datetime.datetime.now(),
                                                to_user_id = juridical_case.main_responsible_id,
                                                comment = request.comment,
                                                message = juridical_case_history['reply_to_new_loan'],
                                                )
    db_session.add(new_juridical_case_history)
    flush_object(db_session)
    
    case = db_session.query(LoanCase).filter(LoanCase.id == request.case_id).first()
        
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

    
    new_loan_case_history = LoanCaseHistory(loan_case_id = request.case_id, general_task_id = request.general_task_id,
                                                from_user_id = request.from_user, created_at = datetime.datetime.now(),
                                                to_user_id = juridical_case.main_responsible_id,
                                                comment = request.comment,
                                                message = problem_case_history['send_to_juridical'],
                                                )
    db_session.add(new_loan_case_history)
    for path in file_path:
        new_file = MonitoringFiles(file_url = path, created_at = datetime.datetime.now())
        db_session.add(new_file)
        flush_object(db_session)
        new_juridical_case_history.files.append(new_file)
        db_session.add(new_juridical_case_history)
        juridical_case.files.append(new_file)
        db_session.add(juridical_case)
        new_loan_case_history.files.append(new_file)
        db_session.add(new_loan_case_history)
    commit_object(db_session)
    
    return {'to_user_id':juridical_case.main_responsible_id}






def change_expired_status(loan_portfolio_id,expired_status, db_session):
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.loan_portfolio_id == loan_portfolio_id)\
        .filter(LoanCase.loan_case_status_id != loan_case['закрыт']).first()
    if get_loan_case is not None:
        get_loan_case.expired_status = expired_status
        
        
        
        
        
        
        


def get_loan_case_details_for_excel(loan_case, db_session):
    loan_case_details = {}
    get_target_status = db_session.query(loan_product).filter(loan_product.name == loan_case.portfolio.loan_product).first()
    loan_case_details ={"loan_portfolio":{"loan_id":loan_case.portfolio.loan_id,
                                        "client_name":loan_case.portfolio.client_name,
                                        "issue_date":loan_case.portfolio.issue_date,
                                        "maturity_date":loan_case.portfolio.maturity_date,
                                        "currency":loan_case.portfolio.currency.name,
                                        "contract_amount": loan_case.portfolio.contract_amount,
                                        "is_target": get_target_status and get_target_status.is_target or None,
                                        "borrower_type":loan_case.portfolio.borrower_type,
                                        "lending_type":loan_case.portfolio.lending_type and loan_case.portfolio.lending_type or None,
                                        "loan_product": loan_case.portfolio.loan_product and loan_case.portfolio.loan_product or None,
                                        "region":loan_case.portfolio.region.name},
                            "main_responsible":{"department":loan_case.main_responsible_id and loan_case.main_responsible.depart.name,
                                          "full_name":loan_case.main_responsible_id and loan_case.main_responsible.full_name,
                                          "region":loan_case.portfolio.region.name},
                            "second_responsible":{"full_name":loan_case.second_responsible and loan_case.second_responsible.full_name,
                                          "region":loan_case.portfolio.region.name},
                            "tasks":TaskManager_class.get_task_manager_by_id(loan_case.task, db_session),
                            "loan_case_status":loan_case.loan_case_status_id and loan_case.status.name or None,
                            "created_at":loan_case.created_at and loan_case.created_at or None,
                            "updated_at":loan_case.updated_at and loan_case.updated_at or None}
        
    return loan_case_details


def get_statistics_for_monitoring(user_id,db_session):
    from_clause_loan_case = f'''FROM loan_case 
                        join loan_portfolio on loan_portfolio.id=loan_case.loan_portfolio_id
                        where
                        (loan_case.main_responsible_id = {user_id}
                        OR loan_case.second_responsible_id = {user_id})'''
                        
    get_sum_loans_foreign_currency = get_sum_loans_for_user(from_clause_loan_case, 'foreign', db_session)
    get_sum_loans_uz_currency = get_sum_loans_for_user(from_clause_loan_case, 'uz', db_session)
    get_loan_case_stats = get_case_data(user_id,'loan_case', db_session)
    
    return {"title":"Статистика для Мониторинга",
            "sum_monitoring_foreign_currency": get_sum_loans_foreign_currency,
            "sum_monitoring_uz_currency":get_sum_loans_uz_currency,
            "monitoring_case_stats":get_loan_case_stats}
    







def get_for_kad(user_id, role, db_session, locals=None):
    print(role)
    for_letter = ''
    if 'kad' in role:
        from_clause_kad_case = f'''FROM kad_case 
                            join loan_portfolio on loan_portfolio.id=kad_case.loan_portfolio_id
                            where
                            (kad_case.main_responsible_id = {user_id}
                            OR kad_case.second_responsible_id = {user_id})
                            AND loan_portfolio.is_taken_kad=true'''
        for_letter = f'and (kad_case.main_responsible_id={user_id} or kad_case.second_responsible_id={user_id})'
        
    elif 'main_superviser_kad' in role:
        from_clause_kad_case = f'''FROM kad_case 
                            join loan_portfolio on loan_portfolio.id=kad_case.loan_portfolio_id
                            WHERE loan_portfolio.is_taken_kad=true'''
        
    elif 'superviser' in role:
        from_clause_kad_case = f'''FROM kad_case 
                            join loan_portfolio on loan_portfolio.id=kad_case.loan_portfolio_id
                            WHERE loan_portfolio.is_taken_kad=true
                            and loan_portfolio.local_code_id {locals}'''
        
    get_sum_kad_foreign_currency = get_sum_loans_for_user(from_clause_kad_case, 'foreign', db_session)
    get_sum_kad_uz_currency = get_sum_loans_for_user(from_clause_kad_case, 'uz', db_session)

    get_kad_case_stats = get_case_data(from_clause_kad_case, 'kad_case', db_session)

    get_hybrid_letter_stats = get_kad_case_hybrid_letter_stats(for_letter, db_session)

    
    return {"title":"Статистика для Департамента КАД",
            "sum_kad_foreign_currency": get_sum_kad_foreign_currency,
            "sum_kad_uz_currency":get_sum_kad_uz_currency,
            "kad_case_stats":get_kad_case_stats,
            "hybrid_letter_stats":get_hybrid_letter_stats}
    


def get_statistics_for_business(user_id, role, db_session, locals=None):
    
    
    if 'business' in role:
        from_clause_business_case = f'''FROM business_case 
                            join loan_portfolio on loan_portfolio.id=business_case.loan_portfolio_id
                            where
                            (business_case.main_responsible_id = {user_id}
                            OR business_case.second_responsible_id = {user_id})
                            AND loan_portfolio.is_taken_business=true'''
        
    elif 'main_superviser_business' in role:
        from_clause_business_case = f'''FROM business_case 
                            join loan_portfolio on loan_portfolio.id=business_case.loan_portfolio_id
                            WHERE loan_portfolio.is_taken_business=true'''
        
    elif 'superviser' in role:
        from_clause_business_case = f'''FROM business_case 
                            join loan_portfolio on loan_portfolio.id=business_case.loan_portfolio_id
                            WHERE loan_portfolio.is_taken_business=true
                            and loan_portfolio.local_code_id {locals}'''
    
    
    
    get_sum_business_foreign_currency = get_sum_loans_for_user(from_clause_business_case, 'foreign', db_session)
    get_sum_business_uz_currency = get_sum_loans_for_user(from_clause_business_case, 'uz', db_session)

    get_business_case_stats = get_case_data(from_clause_business_case,'business_case', db_session)

    return {"sum_business_foreign_currency": get_sum_business_foreign_currency,
            "sum_business_uz_currency":get_sum_business_uz_currency,
            "business_case_stats":get_business_case_stats}





def get_for_problems(user_id, role, db_session, locals=None):
    
    if 'problems' in role:
        from_clause_problems_case = f'''FROM problems_case 
                            join loan_portfolio on loan_portfolio.id=problems_case.loan_portfolio_id
                            where
                            (problems_case.main_responsible_id = {user_id}
                            OR problems_case.second_responsible_id = {user_id})
                            AND loan_portfolio.is_taken_problem=true'''
        
    elif 'main_superviser_problems' in role:
        from_clause_problems_case = f'''FROM problems_case 
                            join loan_portfolio on loan_portfolio.id=problems_case.loan_portfolio_id
                            WHERE loan_portfolio.is_taken_problem=true'''
        
    elif 'superviser' in role:
        from_clause_problems_case = f'''FROM problems_case 
                            join loan_portfolio on loan_portfolio.id=problems_case.loan_portfolio_id
                            WHERE loan_portfolio.is_taken_problem=true
                            and loan_portfolio.local_code_id {locals}'''
    
    
    
    get_sum_problems_foreign_currency = get_sum_loans_for_user(from_clause_problems_case, 'foreign', db_session)
    get_sum_problems_uz_currency = get_sum_loans_for_user(from_clause_problems_case, 'uz', db_session)

    get_problems_case_stats = get_case_data(from_clause_problems_case, 'problems_case', db_session)

    get_non_target = get_non_target_and_out_of_balance_case(user_id, role, db_session, locals)

    
    return {"title":"Статистика для Департамента Проблемных",
            "sum_problems_foreign_currency": get_sum_problems_foreign_currency,
            "sum_problems_uz_currency":get_sum_problems_uz_currency,
            "problems_case_stats":get_problems_case_stats,
            "non_target_and_out_of_balance":get_non_target}




def get_statistics_all_stats(db_session):
    
    get_sum_loans_foreign = db_session.execute(text(f''' SELECT 
                                                sum(case when loan_portfolio.total_overdue is not null then (loan_portfolio.total_overdue::real) else 0 end) AS loan_amount,
                                                sum((case when loan_portfolio.overdue_balance is not null then (loan_portfolio.overdue_balance::real) else 0 end) + 
                                                    (case when loan_portfolio.balance_16377 is not null then (loan_portfolio.balance_16377::real) else 0 end)) as overdue_balance 
                                            from loan_portfolio
                                            where (loan_portfolio.currency_id=90 or loan_portfolio.currency_id=122)
                                            AND loan_portfolio.status=1
                                            ''')).fetchall()
    
    get_sum_loans_uz = db_session.execute(text(f''' SELECT 
                                                sum(case when loan_portfolio.total_overdue is not null and loan_portfolio.total_overdue!='' then (loan_portfolio.total_overdue::real) else 0 end) AS loan_amount,
                                                sum((case when loan_portfolio.overdue_balance is not null and loan_portfolio.overdue_balance!=''  then (loan_portfolio.overdue_balance::real) else 0 end) + 
                                                    (case when loan_portfolio.balance_16377 is not null and loan_portfolio.balance_16377!='' then (loan_portfolio.balance_16377::real) else 0 end)) as overdue_balance 
                                            from loan_portfolio
                                            where loan_portfolio.currency_id=199
                                            AND loan_portfolio.status=1
                                            ''')).fetchall()
    
    loan_stats = {}
    
    get_total_loan = db_session.execute(text(f''' SELECT count(loan_portfolio.id) AS all_count,
                                                    sum(case when loan_portfolio.total_overdue is not null and loan_portfolio.total_overdue!='' then (loan_portfolio.total_overdue::real) else 0 end) as total_overdue,
                                                    sum(case when loan_portfolio.overdue_balance is not null and loan_portfolio.overdue_balance!='' then (loan_portfolio.overdue_balance::real) else 0 end) as overdue_balance,
                                                    sum(case when loan_portfolio.balance_16377 is not null and loan_portfolio.balance_16377!='' then (loan_portfolio.balance_16377::real) else 0 end) as balance_16377,
                                                    sum((case when loan_portfolio.overdue_balance is not null and loan_portfolio.overdue_balance!='' then (loan_portfolio.overdue_balance::real) else 0 end) + 
                                                        (case when loan_portfolio.balance_16377 is not null and loan_portfolio.balance_16377!='' then (loan_portfolio.balance_16377::real) else 0 end)) as all_duty
                                                    from loan_portfolio
                                                    where loan_portfolio.status=1''')).fetchone()
    
   
    loan_stats =  {
            "all_count":get_total_loan.all_count,
            "total_overdue":get_total_loan.total_overdue,
            "overdue_balance":get_total_loan.overdue_balance,
            "balance_16377":get_total_loan.balance_16377,
            "all_duty":get_total_loan.all_duty
            }
    
    
    letter_stats = {}
    sent_letter_count = db_session.execute(text(f'''
                                          select 
                                          count(kad_case.id) as sent_letter_count
                                          from hybrid_letters
                                          join kad_case on kad_case.id=hybrid_letters.kad_case_id
                                          where (hybrid_letters.letter_status_id=2 or hybrid_letters.letter_status_id=5)
                                          ''')).fetchone()
    
    unsent_letter_count = db_session.execute(text(f'''
                                          select 
                                          count(kad_case.id) as unsent_letter_count
                                          from hybrid_letters
                                          join kad_case on kad_case.id=hybrid_letters.kad_case_id
                                          where (hybrid_letters.letter_status_id=1 or hybrid_letters.letter_status_id=3 or hybrid_letters.letter_status_id=4)
                                          ''')).fetchone()
    

    letter_stats= {
            "sent_letter_count":sent_letter_count.sent_letter_count,
            "unsent_letter_count":unsent_letter_count.unsent_letter_count}
    
    
    
    
    
    return {"title":"Статистика по всему банку",
            "sum_uz": get_sum_loans_uz,
            "sum_foreign": get_sum_loans_foreign,
            "loan_stats": loan_stats,
            "letter_stats":letter_stats}



def get_all_stats(user, db_session):
    statistics_all = None
    for roles in user.roles:
        if roles.id == ROLES.has_all_loan_stats.value:
            statistics_all=get_statistics_all_stats(db_session)

    return {"all_statistics": statistics_all}




def get_statistics_for_kad(user, db_session):
    role = []
    statistics_for_kad = None
    statistics_for_target_scheduled_unscheduled = None
    locals=None
    for roles in user.roles:
        if roles.id == ROLES.kad_block_filial_admin.value or roles.id == ROLES.kad_block_filial_user.value or roles.id == ROLES.kad_block_main_admin.value:
            role.append('kad')
        if roles.id == ROLES.main_superviser.value or roles.id == ROLES.main_superviser_kad.value or roles.id == ROLES.main_superviser_kad_with_pledge.value:
            role.append('main_superviser_kad')
        if roles.id == ROLES.superviser.value:
            role.append('superviser')
            locals = get_region_locals(user.region_id, db_session)
        if roles.id == ROLES.superuser.value:
            return {
        "statistics_for_kad": None,
        "statistics_for_target_scheduled_unscheduled":None
        }
    if role!=[]:
        statistics_for_kad=get_for_kad(user.id, role, db_session, locals)
        
        statistics_for_target_scheduled_unscheduled = get_stats_for_target_scheduled_unscheduled(user.id, role, db_session, locals)

    return {
        "statistics_for_kad": statistics_for_kad,
        "statistics_for_target_scheduled_unscheduled":statistics_for_target_scheduled_unscheduled
        }




def get_statistics_for_problem(user, db_session):
    role = []
    locals = None
    statistics_for_problems=None
    for roles in user.roles:
        if roles.id == ROLES.problem_block_filial_admin.value or roles.id == ROLES.promlem_block_filial_user.value or roles.id == ROLES.promlem_block_main_admin.value or roles.id == ROLES.problem_block_lawyer.value:
            role.append('problems')
        if roles.id == ROLES.main_superviser.value or roles.id == ROLES.main_superviser_problem.value:
            role.append('main_superviser_problems')
        if roles.id == ROLES.superviser.value:
            role.append('superviser')
            locals = get_region_locals(user.region_id, db_session)
    
    
    if role!=[]:
        statistics_for_problems = get_for_problems(user.id, role,  db_session, locals)
    return {
        "statistics_for_problems": statistics_for_problems
        }




def get_statistics_for_business(user, db_session):
    role = []
    locals=None
    statistics_for_business=None
    for roles in user.roles:
        if roles.id == ROLES.business_block_filial_admin.value or roles.id == ROLES.business_block_filial_user.value or roles.id == ROLES.business_block_main_admin.value:
            role.append('business')
        if roles.id == ROLES.main_superviser.value or roles.id == ROLES.main_superviser_business.value:
            role.append('main_superviser_business')
        if roles.id == ROLES.superviser.value:
            role.append('superviser')
            locals = get_region_locals(user.region_id, db_session)
    
    
    if role!=[]:
        statistics_for_business = get_statistics_for_business(user.id,role, db_session, locals)
    return {
        "statistics_for_business": statistics_for_business
        }




# def get_statistics(user, db_session):
    
#     role = []
#     if user.department == DEP.KAD.value:
#         statistics_for_kad = None
#         statistics_for_target_scheduled_unscheduled = None
#         locals=None
#         for roles in user.roles:
#             if roles.id == ROLES.kad_block_filial_admin.value or roles.id == ROLES.kad_block_filial_user.value or roles.id == ROLES.kad_block_main_admin.value:
#                 role.append('kad')
#             if roles.id == ROLES.main_superviser.value or roles.id == ROLES.main_superviser_kad.value or roles.id == ROLES.main_superviser_kad_with_pledge.value:
#                 role.append('main_superviser_kad')
#             if roles.id == ROLES.superviser.value:
#                 role.append('superviser')
#                 locals = get_region_locals(user.region_id, db_session)
#             if roles.id == ROLES.superuser.value:
#                 return {
#             "statistics_for_kad": '',
#             "statistics_for_target_scheduled_unscheduled":''
#             }
            
#         statistics_for_kad=get_statistics_for_kad(user.id, role, db_session, locals)
        
#         statistics_for_target_scheduled_unscheduled = get_stats_for_target_scheduled_unscheduled(user.id, role, db_session, locals)

#         return {
#             "statistics_for_kad": statistics_for_kad,
#             "statistics_for_target_scheduled_unscheduled":statistics_for_target_scheduled_unscheduled
#             }
        
        
#     if user.department == DEP.BUSINESS.value:
        
#         locals=None
#         for roles in user.roles:
#             if roles.id == ROLES.business_block_filial_admin.value or roles.id == ROLES.business_block_filial_user.value or roles.id == ROLES.business_block_main_admin.value:
#                 role.append('business')
#             if roles.id == ROLES.main_superviser.value or roles.id == ROLES.main_superviser_business.value:
#                 role.append('main_superviser_business')
#             if roles.id == ROLES.superviser.value:
#                 role.append('superviser')
#                 locals = get_region_locals(user.region_id, db_session)
        
        
        
#         statistics_for_business = get_statistics_for_business(user.id,role, db_session, locals)
#         return {
#             "statistics_for_business": statistics_for_business
#             }
        
#     if user.department == DEP.PROBLEM.value:
        
#         locals = None
#         for roles in user.roles:
#             if roles.id == ROLES.problem_block_filial_admin.value or roles.id == ROLES.promlem_block_filial_user.value or roles.id == ROLES.promlem_block_main_admin.value or roles.id == ROLES.problem_block_lawyer.value:
#                 role.append('problems')
#             if roles.id == ROLES.main_superviser.value or roles.id == ROLES.main_superviser_problem.value:
#                 role.append('main_superviser_problems')
#             if roles.id == ROLES.superviser.value:
#                 role.append('superviser')
#                 locals = get_region_locals(user.region_id, db_session)
        
        
        
#         statistics_for_problems = get_for_problems(user.id, role,  db_session, locals)
#         return {
#             "statistics_for_problems": statistics_for_problems
#             }
                 
#     return 0



def get_region_locals(user_region, db_session):
    
    get_locals = db_session.execute(text(f'''
                                         select id from local_code where region_id={user_region}
                                         ''')).fetchall()
    

    return 'IN '+ str(tuple(item.id for item in get_locals))



def get_sum_loans_for_user(from_clause, currency, db_session):
    
    if currency == 'foreign':
        currency_clause = 'and (loan_portfolio.currency_id=90 or loan_portfolio.currency_id=122)'
    elif currency=='uz':
        currency_clause = 'and loan_portfolio.currency_id=199'
    
    get_sum_loans = db_session.execute(text(f''' SELECT 
                                                sum(case when loan_portfolio.total_overdue is not null then (loan_portfolio.total_overdue::real) else 0 end) AS loan_amount,
                                                sum((case when loan_portfolio.overdue_balance is not null then (loan_portfolio.overdue_balance::real) else 0 end) + 
                                                    (case when loan_portfolio.balance_16377 is not null then (loan_portfolio.balance_16377::real) else 0 end)) as overdue_balance 
                                            {from_clause}
                                            {currency_clause}
                                            AND loan_portfolio.status=1
                                            ''')).fetchall()
    
    
    return get_sum_loans






def get_case_data(from_clause, case, db_session):
    
    
    get_total_case = db_session.execute(text(f''' SELECT count({case}.id) AS all_count,
                                                    sum(case when loan_portfolio.total_overdue is not null then (loan_portfolio.total_overdue::real) else 0 end) as total_overdue,
                                                    sum(case when loan_portfolio.overdue_balance is not null then (loan_portfolio.overdue_balance::real) else 0 end) as overdue_balance,
                                                    sum(case when loan_portfolio.balance_16377 is not null then (loan_portfolio.balance_16377::real) else 0 end) as balance_16377,
                                                    sum((case when loan_portfolio.overdue_balance is not null then (loan_portfolio.overdue_balance::real) else 0 end) + 
                                                        (case when loan_portfolio.balance_16377 is not null then (loan_portfolio.balance_16377::real) else 0 end)) as all_duty
                                                    {from_clause}
                                                    AND loan_portfolio.status=1''')).fetchone()
    
   
    return {
            "all_count":get_total_case.all_count,
            "total_overdue":get_total_case.total_overdue,
            "overdue_balance":get_total_case.overdue_balance,
            "balance_16377":get_total_case.balance_16377,
            "all_duty":get_total_case.all_duty
            }



def get_kad_case_hybrid_letter_stats(for_letter,  db_session):
    
    sent_letter_count = db_session.execute(text(f'''
                                          select 
                                          count(kad_case.id) as sent_letter_count
                                          from hybrid_letters
                                          join kad_case on kad_case.id=hybrid_letters.kad_case_id
                                          where (hybrid_letters.letter_status_id=2 or hybrid_letters.letter_status_id=5)
                                          {for_letter}
                                          ''')).fetchone()
    
    unsent_letter_count = db_session.execute(text(f'''
                                          select 
                                          count(kad_case.id) as unsent_letter_count
                                          from hybrid_letters
                                          join kad_case on kad_case.id=hybrid_letters.kad_case_id
                                          where (hybrid_letters.letter_status_id=1 or hybrid_letters.letter_status_id=3 or hybrid_letters.letter_status_id=4)
                                          {for_letter}
                                          ''')).fetchone()
    

    return {
            "sent_letter_count":sent_letter_count.sent_letter_count,
            "unsent_letter_count":unsent_letter_count.unsent_letter_count}
    
    
    
    
    
    
def get_stats_for_target_scheduled_unscheduled(user_id, role, db_session, locals=None):
    join_portfolio='join loan_portfolio lp on lp.id = lc.loan_portfolio_id'
    from_clause_kad_case = ''
    locals_clause=''
    if 'kad' in role:
        from_clause_kad_case = f'''and (lc.main_responsible_id={user_id} or lc.second_responsible_id={user_id}) '''
        
    
    elif 'superviser' in role:
        join_portfolio = f'''join loan_portfolio lp on lp.id = lc.loan_portfolio_id'''
        locals_clause = f'and lp.local_code_id {locals}' 
    
    
    get_target_stats = db_session.execute(text(f'''
                                              select 
                                                count(msi.id),
                                                msi.name
                                                    from target_monitoring tm
                                                    join monitoring_case mc on mc.target_monitoring_id=tm.id
                                                    join loan_case lc on lc.monitoring_case_id=mc.id
                                                    join monitoring_status msi on tm.target_monitoring_status_id = msi.id
                                                    {join_portfolio} where
                                                    lp.status=1 and lp.is_taken_loan=true and mc.monitoring_case_status_id=1 and lp.total_overdue is not null
                                                    {from_clause_kad_case}
                                                    {locals_clause}
                                                    group by msi.id
                                                    order by msi.id asc
                                               ''')).fetchall()
    
    
    
    get_scheduled_stats = db_session.execute(text(f'''
                                              select 
                                                count(msi.id),
                                                msi.name
                                                    from scheduled_monitoring sm
                                                    join monitoring_case mc on mc.id=sm.monitoring_case_id
                                                    join loan_case lc on lc.monitoring_case_id=mc.id
                                                    join monitoring_status msi on sm.scheduled_monitoring_status_id = msi.id
                                                    {join_portfolio} where
                                                    lp.status=1 and lp.is_taken_loan=true and mc.monitoring_case_status_id=1 and lp.total_overdue is not null
                                                    {from_clause_kad_case}
                                                    {locals_clause}
                                                    group by msi.id
                                                    order by msi.id asc
                                               ''')).fetchall()
    
    
    get_unscheduled_stats = db_session.execute(text(f'''
                                              select 
                                                count(msi.id) count,
                                                msi.name
                                                    from unscheduled_monitoring unsm
                                                    join monitoring_case mc on mc.id=unsm.monitoring_case_id
                                                    join loan_case lc on lc.monitoring_case_id=mc.id
                                                    join monitoring_status msi on unsm.unscheduled_monitoring_status_id = msi.id
                                                    {join_portfolio} where
                                                    lp.status=1 and lp.is_taken_loan=true and mc.monitoring_case_status_id=1 and lp.total_overdue is not null
                                                    {from_clause_kad_case}
                                                    {locals_clause}
                                                    group by msi.id
                                                    order by msi.id asc
                                               ''')).fetchall()
    
    
    
    return {"target_stats":{"count":sum(item[0] for item in get_target_stats),
                            "stats": get_target_stats},
            "scheduled_stats":{"count":sum(item[0] for item in get_scheduled_stats),
                            "stats": get_scheduled_stats},
            "unscheduled_stats":{"count":sum(item[0] for item in get_unscheduled_stats),
                            "stats": get_unscheduled_stats}
            } 
    






def get_non_target_and_out_of_balance_case(user_id, role, db_session, locals):
    
    from_clause_problems_case = ''
    locals_clause=''
    if 'problems' in role:
        from_clause_problems_case = f'''and (pc.main_responsible_id={user_id} or pc.second_responsible_id={user_id})'''
        
    
    elif 'superviser' in role:
        locals_clause = f'and lp.local_code_id {locals}' 
    
    
    
    
    get_non_target = db_session.execute(text(f'''
                                                  select count(pc.id) as count
                                                  from 
                                                  problems_case pc
                                                  join loan_portfolio lp on lp.id=pc.loan_portfolio_id
                                                  where
                                                  lp.is_taken_non_target=true
                                                  and lp.status=1
                                                  {from_clause_problems_case}
                                                  {locals_clause}
                                                  
                                                    ''')).fetchone()
    get_out_of_balance = db_session.execute(text(f'''
                                                  select count(pc.id)
                                                  from 
                                                  problems_case pc
                                                  join loan_portfolio lp on lp.id=pc.loan_portfolio_id
                                                  where
                                                  lp.is_taken_out_of_balance=true
                                                  and lp.status=1
                                                  {from_clause_problems_case}
                                                  {locals_clause}
                                                  
                                                    ''')).fetchone()
    
    
    return {"non_target":get_non_target.count,
            "out_of_balance":get_out_of_balance.count}