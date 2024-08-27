import datetime
from sqlalchemy import or_, and_
from sqlalchemy.sql import func, text
import sqlalchemy
from sqlalchemy.sql.expression import cast
from ....models.loan_case.loan_case_model import LoanCase
from ....models.brief_case.loan_portfolio import Loan_Portfolio
from ....models.brief_case.directories.lending_type import lending_type as portfolio_lending_type
from ....models.monitoring_task_manager.task_manager_model import TaskManager
from ....models.brief_case.directories.loan_product import loan_product
from ..task_manager.task_manager_crud import TaskManager_class
from ....common.commit import commit_object, flush_object
from ....common.is_empty import is_empty, is_empty_list, is_exists
from ....models.monitoring_case.monitoring_case_model import MonitoringCase
from ....models.monitoring_case.target_monitoring_model import TargetMonitoring
from ....models.monitoring_case.scheduled_monitoring_model import ScheduledMonitoring
from ....models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_model import UnscheduledMonitoring
from  app.services.users.users_crud import Users as users
from ....services.loan_monitoring.monitoring_case import scheduled_monitoring_crud
from ....services.loan_monitoring.monitoring_case.unscheduled_monitoring import unscheduled_monitoring_crud
from ....common.dictionaries.monitoring_case_dictionary import monitoring_status
from ....common.dictionaries.departments_dictionary import DEP
from ....common.dictionaries.general_tasks_dictionary import JGT, MGT, PGT, GTCAT



def get_all_loan_case_v2(size, page, region_id, local_code_id, loan_id, client_name,
                      is_target, product_type, client_type, task_status_id, lending_type, client_code, monitoring_stage, monit_status, second_responsible, task_stat,
                      expired, start_period, end_period, user, department, db_session):
    loan_case_list = []
    
    
    case = db_session.query(LoanCase).join(Loan_Portfolio, LoanCase.loan_portfolio_id == Loan_Portfolio.id).filter(Loan_Portfolio.status==1)\
        .filter(Loan_Portfolio.total_overdue!=None).filter(Loan_Portfolio.is_taken_loan==True)
    user_id=user.id
    if user.local_code != 380:
            case = case.filter(LoanCase.second_responsible_id == user_id)
    else:
        case = case.filter(LoanCase.main_responsible_id == user_id)
    
    
    if region_id is not None:
        case = case.filter(Loan_Portfolio.client_region == region_id)
    
    if local_code_id is not None:
        case = case.filter(Loan_Portfolio.local_code_id == local_code_id)
    
    if loan_id is not None or client_name is not None:
        case = case.filter(cast(Loan_Portfolio.loan_id, sqlalchemy.Text).like(f'{loan_id}%'))
    
    if second_responsible is not None:
        case = case.filter(LoanCase.second_responsible_id == second_responsible)
    
    if is_target is not None:
        case = case.filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
        
        if is_target == 0:
            case = case.filter(MonitoringCase.monitoring_case_status_id == 2)
        else:
            case = case.filter(MonitoringCase.monitoring_case_status_id == 1)
            
            case = case.filter(loan_product.name == Loan_Portfolio.loan_product)\
        .filter(loan_product.is_target == is_target)
    
    if product_type is not None:
        case = case.filter(loan_product.name == Loan_Portfolio.loan_product)\
        .filter(loan_product.type == product_type) 
    if lending_type is not None:
        case = case.filter(portfolio_lending_type.name == Loan_Portfolio.lending_type)\
            .filter(portfolio_lending_type.name==lending_type)
    
    if client_type is not None:    
        if client_type != '11' and client_type != '08':
            case = case.filter(Loan_Portfolio.borrower_type.regexp_match('^(?!08|11).*'))
        else:
            case = case.filter(Loan_Portfolio.borrower_type.regexp_match(f'^({client_type}).*'))
    
    if task_status_id is not None:
        case = case.filter(LoanCase.task_manager_id == TaskManager.id).filter(TaskManager.general_task_id == task_status_id)
    if client_code is not None:
        case = case.filter(Loan_Portfolio.loan_account.regexp_match('\d{9}' + str(client_code) + '\d*' + '\d{3}'))
    if expired:
        case = case.filter(MonitoringCase.id == LoanCase.monitoring_case_id).filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.target_monitoring_id == TargetMonitoring.id).filter(MonitoringCase.target_monitoring_id != None)\
                .filter(TargetMonitoring.target_monitoring_result_id == None)\
                .filter(TargetMonitoring.deadline < datetime.datetime.now().date())\
        
        case1 = db_session.query(LoanCase).filter(or_(LoanCase.main_responsible_id == user_id, LoanCase.second_responsible_id == user_id))\
            .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
            .filter(MonitoringCase.id == ScheduledMonitoring.monitoring_case_id)\
            .filter(ScheduledMonitoring.deadline < datetime.datetime.now().date())
        case = case.union(case1)
    
    if monitoring_stage is not None:
        if monitoring_stage == 2:
            case = case.filter(Loan_Portfolio.is_taken_problem == True)
        else: 
            case = case.filter(Loan_Portfolio.is_taken_problem != True)
    
    
    if monit_status  is not None:
        if monit_status == 1:
            case = case.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.target_monitoring_id == TargetMonitoring.id)\
                        .filter(MonitoringCase.monitoring_case_status_id == 1)
            if task_stat is not None:
                case = case.filter(TargetMonitoring.target_monitoring_status_id == task_stat)
                    
    
        elif  monit_status == 2:
            case = case.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.target_monitoring_id == TargetMonitoring.id)\
                    .filter(TargetMonitoring.deadline < datetime.datetime.now().date())\
                    .filter(MonitoringCase.monitoring_case_status_id == 1)
            if task_stat is not None:
                case = case.filter(TargetMonitoring.target_monitoring_status_id == task_stat)
                
        elif monit_status ==3:
            case = case.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.id == ScheduledMonitoring.monitoring_case_id)\
                        .filter(MonitoringCase.monitoring_case_status_id == 1)
            if task_stat is not None:
                case = case.filter(ScheduledMonitoring.scheduled_monitoring_status_id == task_stat)
                
        elif  monit_status == 4:
            case = case.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.id == ScheduledMonitoring.monitoring_case_id)\
                    .filter(ScheduledMonitoring.deadline < datetime.datetime.now().date())\
                        .filter(MonitoringCase.monitoring_case_status_id == 1)\
                        .order_by(ScheduledMonitoring.id.desc())
            if task_stat is not None:
                case = case.filter(ScheduledMonitoring.scheduled_monitoring_status_id == task_stat)
                
        elif monit_status ==5:
            case = case.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.id == UnscheduledMonitoring.monitoring_case_id)\
                    .filter(MonitoringCase.monitoring_case_status_id == 1)
            if task_stat is not None:
                case = case.filter(UnscheduledMonitoring.unscheduled_monitoring_status_id == task_stat)
                
        elif  monit_status == 6:
            case = case.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.id == UnscheduledMonitoring.monitoring_case_id)\
                    .filter(UnscheduledMonitoring.deadline < datetime.datetime.now().date())\
                        .filter(MonitoringCase.monitoring_case_status_id == 1)\
                        .order_by(UnscheduledMonitoring.id.desc())
            if task_stat is not None:
                case = case.filter(UnscheduledMonitoring.unscheduled_monitoring_status_id == task_stat)
    
    
    
    # start_period = '2023-25-08'
    # end_period = '2023-27-08'
    
    if start_period is not None and end_period is not None:
        start_period = datetime.datetime.strptime(start_period, '%Y-%m-%d').date()
        end_period = datetime.datetime.strptime(end_period, '%Y-%m-%d').date()
        case = case.filter(MonitoringCase.id == LoanCase.monitoring_case_id).filter(LoanCase.monitoring_case_id != None)\
            .filter(MonitoringCase.target_monitoring_id == TargetMonitoring.id).filter(MonitoringCase.target_monitoring_id != None)\
            .filter(TargetMonitoring.target_monitoring_result_id == None)\
            .filter(and_(TargetMonitoring.deadline >= start_period, TargetMonitoring.deadline <= end_period))
        
        case1 = db_session.query(LoanCase).filter(or_(LoanCase.main_responsible_id == user_id, LoanCase.second_responsible_id == user_id))\
            .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
            .filter(MonitoringCase.id == ScheduledMonitoring.monitoring_case_id)\
            .filter(ScheduledMonitoring.task_manager_id == TaskManager.id)\
            .filter(and_(ScheduledMonitoring.deadline <= start_period, ScheduledMonitoring.deadline >= end_period))
        case2 = db_session.query(LoanCase).filter(or_(LoanCase.main_responsible_id == user_id, LoanCase.second_responsible_id == user_id))\
            .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
            .filter(MonitoringCase.id == UnscheduledMonitoring.monitoring_case_id)\
            .filter(UnscheduledMonitoring.task_manager_id == TaskManager.id)\
            .filter(and_(UnscheduledMonitoring.deadline <= start_period, UnscheduledMonitoring.deadline >= end_period))
        case = case.union(case1).union(case2)
        
        
    case = case.order_by(LoanCase.updated_at.desc())
      
    count = case.count()
    case = case.limit(size).offset((page-1)*size).all()
    
    for loan in case:
        responsible= {}
        
        
        get_problems_notifications = db_session.execute(text(f'''
                                               select id  from monitoring_notification where split_part(url, ':', 1)='{loan.loan_portfolio_id}'
                                               and to_user_id={user.id}
                                               and notification_type_id in (1,2,3)
                                               and is_read=false 
                                               ''')).fetchall()
        notifications = [notif.id for notif in get_problems_notifications]
        
        
        
        monitoring_stage = get_monitoring_stage(loan, db_session)
        
        if loan.main_responsible.id == user_id:
            responsible = return_responsible(loan.second_responsible)
        else:
            responsible = None
        
        loan_client = loan.portfolio.loan_id
        if loan.portfolio.client_name is not None:
            loan_client = str(loan_client) +' : '+ loan.portfolio.client_name
            
                
        target_deadline_extension_status = ''
        scheduled_deadline_extension_status = ''
        unscheduled_deadline_extension_status = ''
        target_data = make_object('', '', '', '',
                '', '', '', 'Не требуется')
        schedule_data = None
        unscheduled_data = None
        if loan.monitoring_case.monitoring_case_status_id==1:
            
            target_data = get_target_monitoring(loan)
            schedule_data = get_plan_monitoring(loan, db_session)
            unscheduled_data = get_unscheduled_monitoring(loan, db_session)
            target_deadline_extension_status = loan.target_deadline_extension_status_id and loan.target_deadline_extension_status or None
            scheduled_deadline_extension_status = loan.scheduled_deadline_extension_status_id and loan.scheduled_deadline_extension_status or None
            unscheduled_deadline_extension_status = loan.unscheduled_deadline_extension_status_id and loan.unscheduled_deadline_extension_status or None
              
        
        loan_case_list.append({"id":loan.id,
                               "count":notifications,
                               "loan_portfolio": {"id":loan.portfolio.id,
                                                  "total_overdue": loan.portfolio.total_overdue,
                                                  "loan_client":loan_client,
                                                  "local_code":loan.portfolio.local_code.code,
                                                  "loan_id":loan.portfolio.loan_id,
                                                  "client_name":loan.portfolio.client_name,
                                                  },
                               "monitoring_stage":monitoring_stage,
                               "responsible":responsible,
                               "target_data": target_data,
                               "schedule_data": schedule_data,
                               "unscheduled_data": unscheduled_data,
                                "target_deadline_extension_status":target_deadline_extension_status,
                                "scheduled_deadline_extension_status":scheduled_deadline_extension_status,
                                "unscheduled_deadline_extension_status":unscheduled_deadline_extension_status
                                })
    return {"items": loan_case_list,
            "total":count,
            "page":page,
            "size":size} 
    
    
    
    


def return_responsible(responsible):
    return {"id":responsible.id,
            "full_name":responsible and responsible.full_name,
            "region":responsible.region.name,
            "local_code":responsible.local_code}
    
    


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
    
    return monitoring_stage



    
    
def get_target_monitoring(case):
    deadline = None
    task_status = None
    expired = False
    main_responsible_due_date = None
    main_responsible_expired = None
    second_responsible_due_date = None
    second_responsible_expired = None
    
    if case.monitoring_case.target is not None and case.monitoring_case.monitoring_case_status_id==1:
        if case.monitoring_case.target.status.id == monitoring_status["проверено"]:
            return make_object('', case.monitoring_case.target.status.name, '', '',
                                '', '', '', "Целевой")
        else:
            if case.monitoring_case.target.main_responsible_due_date is not None:
                main_responsible_due_date = case.monitoring_case.target.main_responsible_due_date
                if (main_responsible_due_date - case.monitoring_case.target.second_responsible_due_date).days > 2:
                    main_responsible_expired = (main_responsible_due_date - case.monitoring_case.target.second_responsible_due_date).days -2
                
            if case.monitoring_case.target and case.monitoring_case.target.second_responsible_due_date is not None:
                second_responsible_due_date = case.monitoring_case.target.second_responsible_due_date
                if (case.monitoring_case.target.second_responsible_due_date - case.monitoring_case.target.deadline).days > 0:
                    second_responsible_expired = (second_responsible_due_date - case.monitoring_case.target.deadline).days
                
                
            
            task_status = case.monitoring_case.target.status.name
            deadline = case.monitoring_case.target.deadline
                
            if  case.monitoring_case.target.deadline.date() < datetime.datetime.now().date():
                expired = True
    
            return make_object(deadline, task_status, main_responsible_due_date, main_responsible_expired,
                                second_responsible_due_date, second_responsible_expired, expired, "Целевой")
    else:
        return make_object('', '', '', '',
                '', '', '', 'Не требуется')
    
    
    
    
    
def get_plan_monitoring(case, db_session):
    deadline = None
    task_status = None
    main_responsible_due_date = None
    main_responsible_expired = None
    second_responsible_due_date = None
    second_responsible_expired = None
    expired = False
    get_scheduled = scheduled_monitoring_crud.get_last_scheduled(case.monitoring_case_id, db_session)
    if get_scheduled is not None and case.monitoring_case.monitoring_case_status_id==1:
        if get_scheduled.main_responsible_due_date is not None:
            main_responsible_due_date = get_scheduled.main_responsible_due_date
            if (main_responsible_due_date - get_scheduled.second_responsible_due_date).days > 2:
                main_responsible_expired = (main_responsible_due_date - get_scheduled.second_responsible_due_date).days -2
            
        if get_scheduled.second_responsible_due_date is not None:
            second_responsible_due_date = get_scheduled.second_responsible_due_date
            if (get_scheduled.second_responsible_due_date.date() - get_scheduled.deadline).days > 0:
                second_responsible_expired = (second_responsible_due_date.date() - get_scheduled.deadline).days
        
        deadline = get_scheduled.deadline
        task_status = get_scheduled.status.name
        if get_scheduled.status.id !=  monitoring_status["проверено"]:
            if get_scheduled.deadline < datetime.datetime.now().date():
                expired = True
                
        return make_object(deadline, task_status, main_responsible_due_date, main_responsible_expired,
                                second_responsible_due_date, second_responsible_expired, expired, "Плановый")
    else:
        return None
    


def get_unscheduled_monitoring(case, db_session):
    deadline = None
    task_status = None
    main_responsible_due_date = None
    main_responsible_expired = None
    second_responsible_due_date = None
    second_responsible_expired = None
    expired = False
    get_unscheduled = unscheduled_monitoring_crud.get_last_unscheduled(case.monitoring_case_id, db_session)
    if get_unscheduled is not None and case.monitoring_case.monitoring_case_status_id==1:
        if get_unscheduled.main_responsible_due_date is not None:
            main_responsible_due_date = get_unscheduled.main_responsible_due_date
            if (main_responsible_due_date - get_unscheduled.second_responsible_due_date).days > 2:
                main_responsible_expired = (main_responsible_due_date - get_unscheduled.second_responsible_due_date).days -2
            
        if get_unscheduled.second_responsible_due_date is not None:
            second_responsible_due_date = get_unscheduled.second_responsible_due_date
            if (get_unscheduled.second_responsible_due_date.date() - get_unscheduled.deadline).days > 0:
                second_responsible_expired = (second_responsible_due_date.date() - get_unscheduled.deadline).days
        
        deadline = get_unscheduled.deadline
        task_status = get_unscheduled.status.name
        if get_unscheduled.status.id !=  monitoring_status["проверено"]:
            if get_unscheduled.deadline < datetime.datetime.now().date():
                expired = True
            
        return make_object(deadline, task_status, main_responsible_due_date, main_responsible_expired,
                                    second_responsible_due_date, second_responsible_expired, expired, "Внеплан")
    else:
        return None



    
    
    
    
    
    
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
    
    
    



























def get_all_loan_case_v3(size, page, region_id, local_code_id, loan_id, client_name,
                      is_target, product_type, client_type, task_status_id, lending_type, client_code, monitoring_stage, monit_status, second_responsible, task_stat,
                      expired, start_period, end_period, user, department, db_session):
    loan_case_list = []
    case = db_session.query(LoanCase
                            
                            ).join(Loan_Portfolio, LoanCase.loan_portfolio_id == Loan_Portfolio.id)\
                            .filter(Loan_Portfolio.status==1).filter(Loan_Portfolio.is_taken_loan==True)
    user_id=user.id
    if user.local_code != 380:
            case = case.filter(LoanCase.second_responsible_id == user_id).filter(Loan_Portfolio.local_code_id==user.local_code)
    else:
        case = case.filter(LoanCase.main_responsible_id == user_id)
    
    
    if region_id is not None:
        case = case.filter(Loan_Portfolio.client_region == region_id)
    
    if local_code_id is not None:
        case = case.filter(Loan_Portfolio.local_code_id == local_code_id)
    
    if loan_id is not None or client_name is not None:
        case = case.filter(cast(Loan_Portfolio.loan_id, sqlalchemy.Text).like(f'{loan_id}%'))
    
    if second_responsible is not None:
        case = case.filter(LoanCase.second_responsible_id == second_responsible)
    
    if is_target is not None:
        case = case.filter(loan_product.name == Loan_Portfolio.loan_product)\
        .filter(loan_product.is_target == is_target)
    
    if product_type is not None:
        case = case.filter(loan_product.name == Loan_Portfolio.loan_product)\
        .filter(loan_product.type == product_type) 
    if lending_type is not None:
        case = case.filter(portfolio_lending_type.name == Loan_Portfolio.lending_type)\
            .filter(portfolio_lending_type.name==lending_type)
    
    if client_type is not None:    
        if client_type != '11' and client_type != '08':
            case = case.filter(Loan_Portfolio.borrower_type.regexp_match('^(?!08|11).*'))
        else:
            case = case.filter(Loan_Portfolio.borrower_type.regexp_match(f'^({client_type}).*'))
    
    if task_status_id is not None:
        case = case.filter(LoanCase.task_manager_id == TaskManager.id).filter(TaskManager.general_task_id == task_status_id)
    if client_code is not None:
        case = case.filter(Loan_Portfolio.loan_account.regexp_match('\d{9}' + str(client_code) + '\d*' + '\d{3}'))
    if expired:
        case = case.filter(MonitoringCase.id == LoanCase.monitoring_case_id).filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.target_monitoring_id == TargetMonitoring.id).filter(MonitoringCase.target_monitoring_id != None)\
                .filter(TargetMonitoring.target_monitoring_result_id == None)\
                .filter(TargetMonitoring.deadline < datetime.datetime.now().date())\
        
        case1 = db_session.query(LoanCase).filter(or_(LoanCase.main_responsible_id == user_id, LoanCase.second_responsible_id == user_id))\
            .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
            .filter(MonitoringCase.id == ScheduledMonitoring.monitoring_case_id)\
            .filter(ScheduledMonitoring.task_manager_id == TaskManager.id)\
            .filter(ScheduledMonitoring.deadline < datetime.datetime.now().date())
        case = case.union(case1)
    
    if monitoring_stage is not None:
        if monitoring_stage == 2:
            case = case.filter(Loan_Portfolio.is_taken_problem == True)
        else: 
            case = case.filter(Loan_Portfolio.is_taken_problem != True)
    
    
    if monit_status  is not None:
        if monit_status == 1:
            case = case.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.target_monitoring_id == TargetMonitoring.id)\
                        .filter(LoanCase.task_manager_id == TaskManager.id)\
                        .filter(TaskManager.general_task_id == MGT.TARGET_MONITORING.value)
            if task_stat is not None:
                case = case.filter(TargetMonitoring.target_monitoring_status_id == task_stat)
    
        elif  monit_status == 2:
            case = case.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.target_monitoring_id == TargetMonitoring.id)\
                        .filter(LoanCase.task_manager_id == TaskManager.id)\
                        .filter(TaskManager.general_task_id == MGT.TARGET_MONITORING.value)\
                    .filter(TargetMonitoring.deadline < datetime.datetime.now().date())
            if task_stat is not None:
                case = case.filter(TargetMonitoring.target_monitoring_status_id == task_stat)
                
        elif monit_status ==3:
            case = case.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.id == ScheduledMonitoring.monitoring_case_id)\
                     .filter(LoanCase.task_manager_id == TaskManager.id)\
                        .filter(TaskManager.general_task_id == MGT.PLAN_MONITORING.value)
            if task_stat is not None:
                case = case.filter(ScheduledMonitoring.scheduled_monitoring_status_id == task_stat)
                
        elif  monit_status == 4:
            case = case.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.id == ScheduledMonitoring.monitoring_case_id)\
                        .filter(LoanCase.task_manager_id == TaskManager.id)\
                        .filter(TaskManager.general_task_id == MGT.PLAN_MONITORING.value)\
                    .filter(ScheduledMonitoring.deadline < datetime.datetime.now().date())\
                        .order_by(ScheduledMonitoring.id.desc())
            if task_stat is not None:
                case = case.filter(ScheduledMonitoring.scheduled_monitoring_status_id == task_stat)
                
        elif monit_status ==5:
            case = case.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.id == UnscheduledMonitoring.monitoring_case_id)
            if task_stat is not None:
                case = case.filter(UnscheduledMonitoring.unscheduled_monitoring_status_id == task_stat)
                
        elif  monit_status == 6:
            case = case.filter(LoanCase.monitoring_case_id != None)\
                .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
                    .filter(MonitoringCase.id == UnscheduledMonitoring.monitoring_case_id)\
                    .filter(UnscheduledMonitoring.deadline < datetime.datetime.now().date())\
                        .order_by(UnscheduledMonitoring.id.desc())
            if task_stat is not None:
                case = case.filter(UnscheduledMonitoring.unscheduled_monitoring_status_id == task_stat)
    
    
    
    # start_period = '2023-25-08'
    # end_period = '2023-27-08'
    
    if start_period is not None and end_period is not None:
        start_period = datetime.datetime.strptime(start_period, '%Y-%m-%d').date()
        end_period = datetime.datetime.strptime(end_period, '%Y-%m-%d').date()
        case = case.filter(MonitoringCase.id == LoanCase.monitoring_case_id).filter(LoanCase.monitoring_case_id != None)\
            .filter(MonitoringCase.target_monitoring_id == TargetMonitoring.id).filter(MonitoringCase.target_monitoring_id != None)\
            .filter(TargetMonitoring.target_monitoring_result_id == None)\
            .filter(and_(TargetMonitoring.deadline >= start_period, TargetMonitoring.deadline <= end_period))
        
        case1 = db_session.query(LoanCase).filter(or_(LoanCase.main_responsible_id == user_id, LoanCase.second_responsible_id == user_id))\
            .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
            .filter(MonitoringCase.id == ScheduledMonitoring.monitoring_case_id)\
            .filter(ScheduledMonitoring.task_manager_id == TaskManager.id)\
            .filter(and_(ScheduledMonitoring.deadline <= start_period, ScheduledMonitoring.deadline >= end_period))
        case2 = db_session.query(LoanCase).filter(or_(LoanCase.main_responsible_id == user_id, LoanCase.second_responsible_id == user_id))\
            .filter(MonitoringCase.id == LoanCase.monitoring_case_id)\
            .filter(MonitoringCase.id == UnscheduledMonitoring.monitoring_case_id)\
            .filter(UnscheduledMonitoring.task_manager_id == TaskManager.id)\
            .filter(and_(UnscheduledMonitoring.deadline <= start_period, UnscheduledMonitoring.deadline >= end_period))
        case = case.union(case1).union(case2)
        
        
    case = case.order_by(LoanCase.updated_at.desc())
      
    count = case.count()
    case = case.limit(size).offset((page-1)*size).all()
    
    for loan in case:
        responsible= {}
        
        monitoring_stage = get_monitoring_stage(loan, db_session)
        
        if loan.main_responsible.id == user_id:
            responsible = return_responsible(loan.second_responsible)
        else:
            responsible = None
        
        loan_client = loan.portfolio.loan_id
        if loan.portfolio.client_name is not None:
            loan_client = str(loan_client) +' : '+ loan.portfolio.client_name
        # case_data = get_target_monitoring(loan)
        # if case_data['deadline'] == '':
        #     schedule_data = get_plan_monitoring(loan, db_session)
        #     if schedule_data is not None:
        #         case_data = schedule_data
        
        target_deadline_extension_status = ''
        scheduled_deadline_extension_status = ''
        unscheduled_deadline_extension_status = ''
        if loan.monitoring_case.monitoring_case_status_id==1:
            
            target_data = get_target_monitoring(loan)
            schedule_data = get_plan_monitoring(loan, db_session)
            unscheduled_data = get_unscheduled_monitoring(loan, db_session)
            target_deadline_extension_status = loan.target_deadline_extension_status_id and loan.target_deadline_extension_status or None
            scheduled_deadline_extension_status = loan.scheduled_deadline_extension_status_id and loan.scheduled_deadline_extension_status or None
            unscheduled_deadline_extension_status = loan.unscheduled_deadline_extension_status_id and loan.unscheduled_deadline_extension_status or None
            
        loan_case_list.append({"id":loan.id,
                               "loan_portfolio": {"id":loan.portfolio.id,
                                                  "total_overdue": loan.portfolio.total_overdue,
                                                  "loan_client":loan_client,
                                                  "local_code":loan.portfolio.local_code.code,
                                                  "loan_id":loan.portfolio.loan_id,
                                                  "client_name":loan.portfolio.client_name,
                                                  },
                               "monitoring_stage":monitoring_stage,
                               "responsible":responsible,
                               "target_data": target_data,
                               "schedule_data": schedule_data,
                               "unscheduled_data": unscheduled_data,
                                "target_deadline_extension_status":target_deadline_extension_status,
                                "scheduled_deadline_extension_status":scheduled_deadline_extension_status,
                                "unscheduled_deadline_extension_status":unscheduled_deadline_extension_status
                                })
    return {"items": loan_case_list,
            "total":count,
            "page":page,
            "size":size} 
