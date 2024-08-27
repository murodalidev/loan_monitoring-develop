import datetime
from sqlalchemy import or_, case, and_
import sqlalchemy
from sqlalchemy.sql.expression import cast
from ....models.brief_case.directories.loan_product import loan_product
from ....models.monitoring_case.monitoring_case_model import MonitoringCase
from ....models.brief_case.directories.lending_type import lending_type as portfolio_lending_type
from ....models.problems_case.problems_case_model import ProblemsCase
from ....models.juridical_case.juridical_case_model import JuridicalCase
from ....models.monitoring_case.target_monitoring_model import TargetMonitoring
from ....models.monitoring_case.scheduled_monitoring_model import ScheduledMonitoring
from ....models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_model import UnscheduledMonitoring
from ....models.monitoring_task_manager.task_manager_model import TaskManager
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ..task_manager.task_manager_crud import TaskManager_class
from ....models.loan_case.loan_case_model import LoanCase
from ....services.loan_monitoring.monitoring_case import scheduled_monitoring_crud, target_monitoring_crud, unscheduled_monitoring
from ....services.loan_monitoring.monitoring_case.unscheduled_monitoring import unscheduled_monitoring_crud
from ....common.dictionaries.monitoring_case_dictionary import loan_case, monitoring_status
from ..loan_case import loan_case_crud
from ....common.is_empty import  is_empty_list, is_exists
from ....common.commit import commit_object, flush_object
from sqlalchemy import or_
from ....common.dictionaries.departments_dictionary import DEP
from ....common.dictionaries.general_tasks_dictionary import JGT, MGT, PGT, GTCAT

    
def get_monitoring_case(user_id, monitoring_case_id, db_session):
    case = db_session.query(MonitoringCase).filter(LoanCase.monitoring_case_id == MonitoringCase.id)\
        .filter(MonitoringCase.id == monitoring_case_id).first()
    monitoring_cases = {}
    monitoring_case_data = []
    if case is not None:
        #target = case.target_monitoring_id and target_monitoring_crud.get_target_monitoring(user_id, case.target_monitoring_id, db_session)
        scheduled = case.scheduled_monitoring and scheduled_monitoring_crud.get_scheduled_monitoring_details(case.scheduled_monitoring, db_session)
        monitoring_cases = {"id": case.id,
                                "target_monitoring":case.target_monitoring_id,
                                "scheduled_monitoring":scheduled,
                                "monitoring_case_status": case.monitoring_case_status_id and case.status.name or None,
                                "created_at": case.created_at and case.created_at or None,
                                "updated_at": case.updated_at and case.updated_at or None
                                }
    
    return monitoring_cases


def get_monitoring_detail(id, user_id, db_session):
    get_monitoring_case = db_session.query(MonitoringCase).filter(LoanCase.monitoring_case_id == MonitoringCase.id)\
        .filter(MonitoringCase.id == id).first()
    is_exists(get_monitoring_case, 400, 'Monitoring Case not found')
    monitoring_case = []
    
    monitoring_case.append({"id": get_monitoring_case.id,
                                 "target_monitoring_id":get_monitoring_case.target_monitoring_id and get_monitoring_case.target_monitoring_id,
                                 "monitoring_case_status": get_monitoring_case.monitoring_case_status_id and get_monitoring_case.status.name or None,
                                 "created_at": get_monitoring_case.created_at and get_monitoring_case.created_at or None,
                                 "updated_at": get_monitoring_case.updated_at and get_monitoring_case.updated_at or None,
                                 })
        
    return monitoring_case
        
def set_target_monitoring(id, target_monitoring_id, db_session):#used
    get_monitoring_case = db_session.query(MonitoringCase).filter(MonitoringCase.id == id).first()
    
    get_monitoring_case.target_monitoring_id = target_monitoring_id
    get_monitoring_case.updated_at = datetime.datetime.now()
    flush_object(db_session)
    return get_monitoring_case
    
    
    
    
def check_if_empty(monitoriong_case_id, db_session):#used
    get_monitoring_case = db_session.query(MonitoringCase).filter(MonitoringCase.id == monitoriong_case_id)\
        .filter(MonitoringCase.target_monitoring_id == None).first()
        
    is_exists(get_monitoring_case, 400, 'Monitoring Case has already appended target')
    return get_monitoring_case




def get_all_monitoring(page, size, region_id, local_code_id, client_code, loan_id, client_name, is_target,
                       client_type, main_responsible, second_responsible, monitoring_status, task_status, lending_type, user,  db_session):
    user_roles = []
    
    for role in user.roles:
        user_roles.append(role.name)
        
    loan_cases = db_session.query(LoanCase).filter(Loan_Portfolio.id == LoanCase.loan_portfolio_id).filter(Loan_Portfolio.status == 1).filter(Loan_Portfolio.total_overdue!=None)
    
    if 'superviser' in user_roles:
        local_code_id = user.local_code
        
    if 'monitoring_filial_user' in user_roles:
        loan_cases = loan_cases.filter(LoanCase.second_responsible_id == user.id)
    
    if 'monitoring_filial_admin' in user_roles:
        loan_cases = loan_cases.filter(LoanCase.second_responsible_id == user.id)
        
    if 'monitoring_main_admin' in user_roles:
        loan_cases = loan_cases.filter(LoanCase.main_responsible_id == user.id)
        
    if main_responsible is not None:
        if 'main_superviser' in user_roles or 'main_superviser_kad' in user_roles:
            loan_cases = loan_cases.filter(LoanCase.main_responsible_id == main_responsible)
    
    if region_id is not None:
        loan_cases = loan_cases.filter(Loan_Portfolio.client_region == region_id)
        
    if lending_type is not None:
        loan_cases = loan_cases.filter(portfolio_lending_type.name == Loan_Portfolio.lending_type)\
            .filter(portfolio_lending_type.name==lending_type)
        
    if local_code_id is not None:
        loan_cases = loan_cases.filter(Loan_Portfolio.local_code_id == local_code_id)
    
    if client_code is not None:
            loan_cases = loan_cases.filter(LoanCase.loan_portfolio_id == Loan_Portfolio.id).filter(Loan_Portfolio.loan_account.regexp_match('\d{9}' + str(client_code) + '\d*' + '\d{3}'))

    if loan_id is not None or client_name is not None:
        loan_cases = loan_cases.filter(or_(cast(Loan_Portfolio.loan_id, sqlalchemy.Text).like(f'{loan_id}%'), Loan_Portfolio.client_name.ilike(f'%{client_name}%')))
    
    if second_responsible is not None:
        loan_cases = loan_cases.filter(LoanCase.second_responsible_id == second_responsible)
    
    if is_target is not None:
        loan_cases = loan_cases.filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
        
        if is_target == 0:
            loan_cases = loan_cases.filter(MonitoringCase.monitoring_case_status_id == 2)
        else:
            loan_cases = loan_cases.filter(MonitoringCase.monitoring_case_status_id == 1)
            
            loan_cases = loan_cases.filter(loan_product.name == Loan_Portfolio.loan_product)\
        .filter(loan_product.is_target == is_target)
        
    if client_type is not None:    
        if client_type != '11' and client_type != '08':
            loan_cases = loan_cases.filter(Loan_Portfolio.borrower_type.regexp_match('^(?!08|11).*'))
        else:
            loan_cases = loan_cases.filter(Loan_Portfolio.borrower_type.regexp_match(f'^({client_type}).*'))
            
    if monitoring_status  is not None:
        print(monitoring_status)
        if monitoring_status == 1:
            loan_cases = loan_cases.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.target_monitoring_id == TargetMonitoring.id)\
                    .filter(TargetMonitoring.task_manager_id == TaskManager.id)\
                        .filter(MonitoringCase.monitoring_case_status_id == 1)
            if task_status is not None:
                loan_cases = loan_cases.filter(TargetMonitoring.target_monitoring_status_id == task_status)
    
        elif  monitoring_status == 2:
            loan_cases = loan_cases.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.target_monitoring_id == TargetMonitoring.id)\
                            .filter(TargetMonitoring.task_manager_id == TaskManager.id)\
                                .filter(MonitoringCase.monitoring_case_status_id == 1)\
                    .filter(TargetMonitoring.deadline < datetime.datetime.now().date())
            if task_status is not None:
                loan_cases = loan_cases.filter(TargetMonitoring.target_monitoring_status_id == task_status)
                
        elif monitoring_status ==3:
            loan_cases = loan_cases.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.id == ScheduledMonitoring.monitoring_case_id)\
                        .filter(ScheduledMonitoring.task_manager_id == TaskManager.id)\
                            .filter(MonitoringCase.monitoring_case_status_id == 1)\
                        .order_by(ScheduledMonitoring.id.desc())
            if task_status is not None:
                loan_cases = loan_cases.filter(ScheduledMonitoring.scheduled_monitoring_status_id == task_status)
                
        elif  monitoring_status == 4:
            loan_cases = loan_cases.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.id == ScheduledMonitoring.monitoring_case_id)\
                        .filter(ScheduledMonitoring.task_manager_id == TaskManager.id)\
                            .filter(MonitoringCase.monitoring_case_status_id == 1)\
                    .filter(ScheduledMonitoring.deadline < datetime.datetime.now().date())\
                        .order_by(ScheduledMonitoring.id.desc())
            if task_status is not None:
                loan_cases = loan_cases.filter(ScheduledMonitoring.scheduled_monitoring_status_id == task_status)
        elif monitoring_status ==5:
            loan_cases = loan_cases.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.id == UnscheduledMonitoring.monitoring_case_id)\
                        .filter(MonitoringCase.monitoring_case_status_id == 1)
            if task_status is not None:
                loan_cases = loan_cases.filter(UnscheduledMonitoring.unscheduled_monitoring_status_id == task_status)
                
        elif  monitoring_status == 6:
            loan_cases = loan_cases.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.id == UnscheduledMonitoring.monitoring_case_id)\
                        .filter(MonitoringCase.monitoring_case_status_id == 1)\
                    .filter(UnscheduledMonitoring.deadline < datetime.datetime.now().date())\
                        .order_by(UnscheduledMonitoring.id.desc())
            if task_status is not None:
                loan_cases = loan_cases.filter(UnscheduledMonitoring.unscheduled_monitoring_status_id == task_status)
                
    loan_cases = loan_cases.order_by(LoanCase.updated_at.desc())
    count = loan_cases.count()
    loan_cases = loan_cases.limit(size).offset((page-1)*size).all()
    #return get_monitoring_case_dict_for_excel(loan_cases, db_session)
    return  {"items": get_monitoring_case_dict(loan_cases, monitoring_status, task_status, db_session),
            "total":count,
            "page":page,
            "size":size,
            "statistics": get_statistics_for_monitoring(local_code_id, second_responsible, db_session)} 
    
    
    
    
def get_monitoring_case_dict(loan_cases, monitoring_status, status, db_session):
    monitoring_cases = []
    for case in loan_cases:
        data = get_monitoring_stage(case, db_session)
        deadline = {"deadline": '',
            "monitoring_status": 'Не требуется',
            "task_status": '',
            "main_responsible_due_date": '',
            "main_responsible_expired": '',
            "second_responsible_due_date": '',
            "second_responsible_expired": '',
            "expired": ''}
        
        if case.monitoring_case.monitoring_case_status_id==1:
        
            if monitoring_status == 1 or monitoring_status == 2:
                deadline = get_target_monitoring_deadline(case)
            elif monitoring_status == 3 or monitoring_status == 4:
                deadline = get_plan_monitoring_deadline(case, db_session, status)
            else:
                deadline = get_target_monitoring_deadline(case)
                if deadline['deadline'] is None:
                    deadline = get_plan_monitoring_deadline(case, db_session, status)
        
        monitoring_cases.append({
            "loan_case_id": case.id,
            "loan_portfolio_id": case.portfolio.id,
            "loan_id":case.portfolio.loan_id,
            "client_name": case.portfolio.client_name,
            "total_overdue": case.portfolio.total_overdue,
            "region": case.portfolio.client_region and case.portfolio.region or None,
            "local_code": case.portfolio.local_code_id and case.portfolio.local_code.code or None,
            "main_responsible":{"id":case.main_responsible and case.main_responsible.id,
                                          "full_name":case.main_responsible and case.main_responsible.full_name},
            "second_responsible":{"id":case.second_responsible and case.second_responsible.id,
                                          "full_name":case.second_responsible and case.second_responsible.full_name},
            "monitoring_stage": data['monitoring_stage'],
            "task_status":deadline['task_status'],
            "monitoring_status":deadline['monitoring_status'],
            "main_responsible_due_date": deadline['main_responsible_due_date'],
            "main_responsible_expired": deadline['main_responsible_expired'],
            "second_responsible_due_date": deadline['second_responsible_due_date'],
            "second_responsible_expired": deadline['second_responsible_expired'],
            "expired":deadline['expired'] and deadline['expired'],
            "deadline": deadline['deadline'] and deadline['deadline'],
            "created_at": case.created_at
        })
        
    return monitoring_cases



def get_monitoring_stage(case, db_session):
    tasks = TaskManager_class.get_task_manager_by_id(case.task, db_session)
    if (case.portfolio.is_taken_problem and case.portfolio.is_taken_juridic) or\
        (not case.portfolio.is_taken_problem and case.portfolio.is_taken_juridic) or\
            (not case.portfolio.is_taken_juridic and tasks['general_task']['id'] == MGT.SEND_JURIDIC.value):
        monitoring_stage = 'Юристы'
    elif (case.portfolio.is_taken_problem and not case.portfolio.is_taken_juridic == False) or\
        (case.portfolio.is_taken_problem and not case.portfolio.is_taken_loan == False) or\
            (not case.portfolio.is_taken_problem and tasks['general_task']['id'] == MGT.SEND_PORBLEM.value):
        monitoring_stage = 'Проблемные активы'
    else:
        monitoring_stage = 'Мониторинг'
    
    return {'monitoring_stage': monitoring_stage}
    
    
def get_target_monitoring_deadline(case):
    deadline = None
    monitoring_status = None
    task_status = None
    expired = False
    exp_days = None
    main_responsible_due_date = None
    main_responsible_expired = None
    second_responsible_due_date = None
    second_responsible_expired = None
    if case.monitoring_case.target is not None:
        if case.monitoring_case.target.main_responsible_due_date is not None:
            main_responsible_due_date = case.monitoring_case.target.main_responsible_due_date
            if (main_responsible_due_date - case.monitoring_case.target.second_responsible_due_date).days > 2:
                main_responsible_expired = (main_responsible_due_date - case.monitoring_case.target.second_responsible_due_date).days -2
            
        if case.monitoring_case.target and case.monitoring_case.target.second_responsible_due_date is not None:
            second_responsible_due_date = case.monitoring_case.target.second_responsible_due_date
            if (case.monitoring_case.target.second_responsible_due_date - case.monitoring_case.target.deadline).days > 0:
                second_responsible_expired = (second_responsible_due_date - case.monitoring_case.target.deadline).days
            
            
        if case.monitoring_case and case.monitoring_case.target:
            task_status = case.monitoring_case.target.status.name
            deadline = case.monitoring_case.target.deadline
            
            if case.expired_status:
                monitoring_status = 'Целевой с просрочкой'
                expired = True
            else:
                monitoring_status = 'Целевой мониторинг'
        if not case.monitoring_case.target:
            monitoring_status = 'Мониторинг не требуется'
    return {"deadline": deadline,
            "monitoring_status": monitoring_status,
            "task_status":task_status,
            "main_responsible_due_date": main_responsible_due_date,
            "main_responsible_expired": main_responsible_expired,
            "second_responsible_due_date": second_responsible_due_date,
            "second_responsible_expired": second_responsible_expired,
            "expired": expired}
    

def get_plan_monitoring_deadline(case, db_session,  status=None):
    deadline = ''
    monitoring_status = ''
    task_status = ''
    main_responsible_due_date = None
    main_responsible_expired = None
    second_responsible_due_date = None
    second_responsible_expired = None
    expired = False
    get_scheduled = scheduled_monitoring_crud.get_last_scheduled(case.monitoring_case_id, db_session, status)
    if get_scheduled is not None:
        main_responsible_due_date = get_scheduled.main_responsible_due_date
        second_responsible_due_date = get_scheduled.second_responsible_due_date
        deadline = get_scheduled.deadline
        task_status = get_scheduled.status.name
        if get_scheduled.deadline < datetime.datetime.now().date():
            monitoring_status = 'Плановый с просрочкой'
            expired = True
        else:
            monitoring_status = 'Плановый мониторинг'
    if not case.monitoring_case.target:
        monitoring_status = 'Мониторинг не требуется'
    return {"deadline": deadline,
            "monitoring_status": monitoring_status,
            "task_status": task_status,
            "main_responsible_due_date": main_responsible_due_date,
            "main_responsible_expired": main_responsible_expired,
            "second_responsible_due_date": second_responsible_due_date,
            "second_responsible_expired": second_responsible_expired,
            "expired": expired}
  



    
def get_monitoring_case_dict_for_excel(case, db_session):
    monitoring_cases = {}
    
    data = get_monitoring_stage(case, db_session)
    deadline = []
    deadline = get_target_monitoring_deadline(case, db_session)
    if deadline["deadline"] is None:
        deadline = get_plan_monitoring_deadline(case, db_session)
    monitoring_cases = {
        "monitoring_status":deadline['monitoring_status'],
        "task_status":deadline['task_status'],
        "expired":deadline['expired'] and deadline['expired'],
        "deadline": deadline['deadline'] and deadline['deadline'],
        "main_responsible_due_date": deadline['main_responsible_due_date'],
        "second_responsible_due_date": deadline['second_responsible_due_date'],
        "created_at": case.created_at
    }
        
    return monitoring_cases





def get_statistics_for_monitoring(local_code_id, second_responsible, db_session):
    loan_cases = db_session.query(LoanCase)\
        .join(ProblemsCase, ProblemsCase.loan_portfolio_id == LoanCase.loan_portfolio_id, isouter=True)\
            .join(JuridicalCase, JuridicalCase.loan_portfolio_id == LoanCase.loan_portfolio_id, isouter=True)\
        .filter(ProblemsCase.id == None).filter(JuridicalCase.id == None)
        
    scheduled = db_session.query(ScheduledMonitoring).filter(MonitoringCase.id == ScheduledMonitoring.monitoring_case_id)\
            .filter(LoanCase.monitoring_case_id == MonitoringCase.id)\
                .filter(LoanCase.loan_portfolio_id == Loan_Portfolio.id)\
                
    
    target = db_session.query(TargetMonitoring).filter(MonitoringCase.target_monitoring_id == TargetMonitoring.id)\
            .filter(LoanCase.monitoring_case_id == MonitoringCase.id)\
                .filter(LoanCase.loan_portfolio_id == Loan_Portfolio.id)\
    
    problems = db_session.query(ProblemsCase).join(JuridicalCase, JuridicalCase.loan_portfolio_id == ProblemsCase.loan_portfolio_id, isouter=True)\
        .filter(JuridicalCase.id == None).filter(LoanCase.loan_portfolio_id == ProblemsCase.loan_portfolio_id)
        
    juridic = db_session.query(JuridicalCase).filter(LoanCase.loan_portfolio_id == JuridicalCase.loan_portfolio_id)
    
    
    if local_code_id is not None:
        loan_cases = loan_cases.filter(Loan_Portfolio.id == LoanCase.loan_portfolio_id).filter(Loan_Portfolio.local_code_id == local_code_id)
        # print(str(loan_cases))
        # exit()
    
        scheduled = scheduled.filter(Loan_Portfolio.local_code_id == local_code_id)
        
        target = target.filter(Loan_Portfolio.local_code_id == local_code_id)
        
        problems = problems.filter(Loan_Portfolio.id == ProblemsCase.loan_portfolio_id).filter(Loan_Portfolio.local_code_id == local_code_id)
        juridic = juridic.join(Loan_Portfolio).filter(Loan_Portfolio.local_code_id == local_code_id)
    if second_responsible is not None:
        loan_cases = loan_cases.filter(LoanCase.second_responsible_id == second_responsible)
        problems = problems.filter(LoanCase.second_responsible_id == second_responsible)
        juridic = juridic.filter(LoanCase.second_responsible_id == second_responsible)
        target = target.filter(LoanCase.second_responsible_id == second_responsible)
        scheduled = scheduled.filter(LoanCase.second_responsible_id == second_responsible)
        
    loan_cases = loan_cases.count()
    problems = problems.count()
    juridic = juridic.count()
    scheduled = scheduled.filter(ScheduledMonitoring.deadline < datetime.datetime.now().date()).count()
    target = target.filter(TargetMonitoring.target_monitoring_result_id == None).filter(TargetMonitoring.deadline < datetime.datetime.now()).count()
        
    monitoring_expired = scheduled + target
    
    return{"loan_cases": loan_cases,
           "expired": monitoring_expired,
           "problems": problems,
           "juridic": juridic}