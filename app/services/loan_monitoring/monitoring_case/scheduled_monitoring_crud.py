import datetime

from app.models.monitoring_case.reslut_reason_model import ResultReason
from app.models.statuses.monitoring_frequency_period_model import MonitoringFrequencyPeriod
from ....models.files.monitoring_files_model import MonitoringFiles
from ....models.monitoring_case.monitoring_case_model import MonitoringCase
from ....models.loan_case.loan_case_model import LoanCase
from ....models.loan_case.loan_case_history_model import LoanCaseHistory
from ....models.monitoring_case.scheduled_monitoring_history_model import ScheduledMonitoringHistory
from ....models.monitoring_case.scheduled_monitoring_model import ScheduledMonitoring
from ....models.monitoring_case.scheduled_monitoring_expiration_model import ScheduledMonitoringExpiration
from ....models.statuses.monitoring_frequency_period_model import MonitoringFrequencyPeriod
from ....common.is_empty import is_empty, is_exists
from ....common.commit import commit_object, flush_object
from .script_date_holidays import get_business_days
from dateutil.relativedelta import relativedelta
from ....common import save_file
from ....schemas.juridical_case_schemas import SendToProblemAfterTarget
from ..juridical_case import juridical_case_crud
from ...monitoring_files import files_crud
from ..task_manager.task_manager_crud import TaskManager_class
from ....common.dictionaries.monitoring_case_dictionary import  monitoring_status
from ....common.dictionaries.notification_dictionary import notification_type, notification_body
from ....common.dictionaries.case_history_dictionaries import loan_case_history
from ....common.dictionaries.task_status_dictionaries import task_status
from ....schemas.task_manager_schemas import CreateTaskManagerSetTargetMonitoring,UpdateTaskManagerSendToCheck, UpdateTaskManagerAccept, GetaskManager,UpdateTaskManagerClose
from ..notification.notification_crud import Notificaton_class
from ....schemas.notification_schemas import CreateNotification
from ....config.logs_config import info_logger
import os
from ..problems_case import non_targeted_case
from ....common.dictionaries.general_tasks_dictionary import JGT, MGT, MAIN_DUE_DATE, CASE_HISTORY, DEADLINE_EXT


def appoint_scheduled_monitoring(request, db_session):
    info_logger.info("user %s required 'appoint_scheduled_monitoring' method", request.main_responsible_id)
    #check_if_exists(request.monitoring_case_id, db_session)
    result  = get_frequency_period_by_date(request.frequency_period_id, request.loan_issue_date, db_session)
    data = CreateTaskManagerSetTargetMonitoring()
    data.general_task_id = request.general_task_id
    task = TaskManager_class(data)
    new_task = task.create_task_manager_when_set_scheduled_monitoring(db_session)
    
    new_scheduled_monitoring = ScheduledMonitoring(monitoring_case_id = request.monitoring_case_id,
                                             scheduled_monitoring_status_id = monitoring_status['назначен'],
                                             frequency_period_id = request.frequency_period_id,
                                             task_manager_id  = new_task.id,
                                             created_at = datetime.datetime.now().date(),
                                             deadline = result['deadline'])
    
    db_session.add(new_scheduled_monitoring)
    flush_object(db_session)
    new_scheduled_monitoring.monitoring_case.loan_case[0].updated_at = datetime.datetime.now()
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == request.loan_case_id).first()
    data = UpdateTaskManagerAccept()
    data.task_manager_id = get_loan_case.task_manager_id
    data.task_status = task_status['завершено'],
    task = TaskManager_class(data)
    task.update_task_manager(db_session) 
    
    data = CreateNotification()
    data.from_user_id = request.main_responsible_id
    data.to_user_id = request.second_responsible_id
    data.notification_type = notification_type['scheduled_monitoring']
    data.body = notification_body['appoint_scheduled_monitoring']
    data.url = f'{get_loan_case.loan_portfolio_id}' + ':' + f'{get_loan_case.id}'+ ':' +f'{MGT.PLAN_MONITORING.value}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    new_loan_case_history = ScheduledMonitoringHistory(monitoring_case_id = new_scheduled_monitoring.monitoring_case_id, 
                                            type_id = CASE_HISTORY.SCHEDULED.value,
                                            from_user_id = request.main_responsible_id, 
                                            to_user_id= request.second_responsible_id,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = loan_case_history['appoint_scheduled']
                                                )
    db_session.add(new_loan_case_history)
    commit_object(db_session)
    
    return {"OK"}



def appoint_scheduled_monitoringv2(request, db_session):
    check_if_exists(request.monitoring_case_id, db_session)
    result  = get_frequency_period_by_date(request.frequency_period_id, db_session)
    new_scheduled_monitoring = ScheduledMonitoring(monitoring_case_id = request.monitoring_case_id,
                                             scheduled_monitoring_status_id = monitoring_status['назначен'],
                                             frequency_period_id = request.frequency_period_id,
                                             created_at = result['created_at'],
                                             deadline = result['deadline'])
    
    db_session.add(new_scheduled_monitoring)
    flush_object(db_session)

    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == request.loan_case_id).first()
    
    data = UpdateTaskManagerClose()
    data.task_manager_id = get_loan_case.task_manager_id
    data.general_task_id = request.general_task_id
    data.task_status = task_status['начато']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)

    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == request.loan_case_id).first()
    
    data = CreateNotification()
    data.from_user_id = request.main_responsible_id
    data.to_user_id = request.second_responsible_id
    data.notification_type = notification_type['scheduled_monitoring']
    data.body = notification_body['appoint_scheduled_monitoring']
    data.url = f'{get_loan_case.loan_portfolio_id}' + ':' + f'{get_loan_case.id}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    new_loan_case_history = LoanCaseHistory(loan_case_id = request.loan_case_id,
                                            type_id = CASE_HISTORY.LOAN_CASE.value,
                                            general_task_id = request.general_task_id,
                                            from_user_id = request.main_responsible_id, 
                                            to_user_id= request.second_responsible_id,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = loan_case_history['appoint_scheduled']
                                                )
    db_session.add(new_loan_case_history)
    
    
    
    commit_object(db_session)
    
    return {"OK"}


import calendar

def get_frequency_period_by_date(frequency_period, loan_issue_date, db_session):
    
    freq_per = db_session.query(MonitoringFrequencyPeriod).filter(MonitoringFrequencyPeriod.id == frequency_period).first()
    date_now = datetime.datetime.now().date()
    
    prev_year = datetime.datetime.now().year - 1
    first_day_of_november = datetime.datetime(prev_year, 11, 1).date()
    created_at = datetime.datetime.strptime(loan_issue_date, '%Y-%m-%d').date()
    days_in_month = calendar.monthrange(first_day_of_november.year, first_day_of_november.month)[1]
    last_day_of_month = datetime.datetime(first_day_of_november.year, first_day_of_november.month, days_in_month)
    deadline =  (last_day_of_month + relativedelta(months=freq_per.code)).date()
    
    i=0
    
    while True:
        if date_now < deadline or i>100:
            break
        if frequency_period == 1:
            deadline = last_day_of_month + relativedelta(months=freq_per.code) + relativedelta(months=12)
        else:
            deadline = deadline + relativedelta(months=freq_per.code)
        i=i+1
    return {'created_at':created_at, 
            'deadline': deadline}


    # freq_per = db_session.query(MonitoringFrequencyPeriod).filter(MonitoringFrequencyPeriod.id == frequency_period).first()
    # date_now = datetime.datetime.now().date()
    # current_year = datetime.datetime.now().year 
    
    # first_day_of_january = datetime.datetime(current_year, 1, 1).date() - relativedelta(months=2)
    # created_at = datetime.datetime.strptime(loan_issue_date, '%Y-%m-%d').date()
    # deadline =  first_day_of_january + relativedelta(months=freq_per.code)
    # i=0
    
    # while True:
    #     if date_now < deadline or i>100:
    #         break
    #     deadline = deadline + relativedelta(months=freq_per.code)
    #     i=i+1
    # return {'created_at':created_at, 
    #         'deadline': deadline}



def accept__or_rework_scheduled_monitoring(request, db_session):
    info_logger.info("user %s required 'accept__or_rework_scheduled_monitoring' method", request.from_user)
    scheduled = db_session.query(ScheduledMonitoring).filter(ScheduledMonitoring.id == request.scheduled_monitoring_id).first()
    
    # data = GetaskManager()
    # data.task_manager_id = request.task_manager_id
    # task = TaskManager_class(data)
    # get_task = task.get_task_by_id(db_session)
    # general_task = get_task.general_task_id
    
    if request.result_type:
        message = loan_case_history['accepted_scheduled']
        if scheduled.scheduled_monitoring_result_id == 2 or scheduled.scheduled_monitoring_result_id == 3:
            
            problem_data = SendToProblemAfterTarget()
            problem_data.general_task_id = MGT.SEND_JURIDIC.value
            problem_data.case_id = scheduled.monitoring_case.loan_case[0].id
            problem_data.intended_overdue_type_id = scheduled.scheduled_monitoring_result_id
            problem_data.amount = scheduled.amount
            problem_data.loan_portfolio_id = scheduled.monitoring_case.loan_case[0].portfolio.id
            problem_data.local_code_id = scheduled.monitoring_case.loan_case[0].portfolio.local_code_id
            problem_data.comment = request.comment and request.comment
            problem_data.from_user = request.from_user
            info_logger.info("user %s required sent scheduled_monitoring to juridic", request.from_user)
            non_targeted_case.create_problems_non_target(problem_data, scheduled.monitoring_case.loan_case[0].main_responsible.depart.id, scheduled.files, db_session)
            
            
            
        else:  
            result  = get_frequency_period_by_date(scheduled.frequency_period_id, str(scheduled.deadline), db_session)
            new_scheduled = ScheduledMonitoring(monitoring_case_id = scheduled.monitoring_case_id,
                                             scheduled_monitoring_status_id = monitoring_status['назначен'],
                                             frequency_period_id = scheduled.frequency_period_id,
                                             task_manager_id  = scheduled.task.id,
                                             created_at = datetime.datetime.now().date(),
                                             deadline = result['deadline'])
    
            db_session.add(new_scheduled)
            flush_object(db_session)
            
        status = monitoring_status['проверено']
        scheduled.monitoring_case.loan_case[0].scheduled_deadline_extension_status_id = DEADLINE_EXT.OK.value
        body = notification_body['accept_scheduled_monitoring']
        data = UpdateTaskManagerAccept()
        data.task_manager_id = request.task_manager_id
        data.task_status = task_status['принят_ответственным']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
        info_logger.info("user %s accepted scheduled_monitoring", request.from_user)
        
    else:
        status = monitoring_status['переделать']
        message = loan_case_history['rejected_scheduled']
        body = notification_body['rework_scheduled_monitoring']
        data = UpdateTaskManagerAccept()
        data.task_manager_id = request.task_manager_id
        data.task_status = task_status['переделать']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
        file_path = files_crud.set_wrong_files(request.wrong_files, scheduled, db_session)
        db_session.add(scheduled)
        info_logger.info("user %s sent scheduled_monitoring to rework", request.from_user)
        info_logger.info("user %s sent to rework files: %s", request.from_user, file_path)
        
    scheduled.scheduled_monitoring_status_id = status
    scheduled.main_responsible_due_date = datetime.datetime.now()
    scheduled.monitoring_case.loan_case[0].updated_at = datetime.datetime.now()
    
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == request.loan_case_id).first()
    #if scheduled.scheduled_monitoring_result_id != None and (datetime.datetime.now().date() - scheduled.second_responsible_due_date.date()).days > MAIN_DUE_DATE.DATE.value:
    if scheduled.scheduled_monitoring_result_id != None and (get_business_days(datetime.datetime.now().date(), MAIN_DUE_DATE.DATE.value, db_session) - scheduled.second_responsible_due_date.date()).days > 0:
        
        new_expiration = ScheduledMonitoringExpiration(scheduled_monitoring_id = scheduled.id,
                                                    responsible_id = request.from_user,
                                                    deadline_date = scheduled.deadline,
                                                    due_date = datetime.datetime.now(),
                                                    created_at = datetime.datetime.now())
    
        db_session.add(new_expiration)
    
    
    new_loan_case_history = ScheduledMonitoringHistory(monitoring_case_id = scheduled.monitoring_case_id, 
                                            type_id = CASE_HISTORY.SCHEDULED.value,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = message
                                                )
    
    db_session.add(new_loan_case_history)
    data = CreateNotification()
    data.from_user_id = request.from_user 
    data.to_user_id =request.to_user
    data.notification_type = notification_type['scheduled_monitoring']
    data.body = body
    data.url = f'{get_loan_case.loan_portfolio_id}' + ':' + f'{get_loan_case.id}'+ ':' +f'{MGT.PLAN_MONITORING.value}'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    
    
    commit_object(db_session)
    
    return "OK"





def accept_or_rework_scheduled_monitoringv2(request, db_session):
    scheduled = db_session.query(ScheduledMonitoring).filter(ScheduledMonitoring.id == request.scheduled_monitoring_id).first()
    
    data = GetaskManager()
    data.task_manager_id = request.task_manager_id
    task = TaskManager_class(data)
    get_task = task.get_task_by_id(db_session)
    general_task = get_task.general_task_id
    
    if request.result_type:
        status = monitoring_status['принят']
        additional_data = {'scheduled_monitoring_status': 'принят'}
        message = loan_case_history['accepted_scheduled']
        body = notification_body['accept_scheduled_monitoring']
        data = UpdateTaskManagerAccept()
        data.task_manager_id = request.task_manager_id
        data.task_status = task_status['завершено']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
    else:
        status = monitoring_status['переделать']
        additional_data = {'target_monitoring_status': 'переделать'}
        message = loan_case_history['rejected_scheduled']
        body = notification_body['rework_scheduled_monitoring']
        data = UpdateTaskManagerAccept()
        data.task_manager_id = request.task_manager_id
        data.task_status = task_status['переделать']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
        scheduled.files.clear()
        db_session.add(scheduled)
    scheduled.scheduled_monitoring_status_id = status
    
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == request.loan_case_id).first()
    data = CreateNotification()
    data.from_user_id = request.from_user 
    data.to_user_id =request.to_user
    data.notification_type = notification_type['scheduled_monitoring']
    data.body = body
    data.url = f'{get_loan_case.loan_portfolio_id}' + ':' + f'{get_loan_case.id}'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    new_loan_case_history = LoanCaseHistory(loan_case_id = request.loan_case_id, 
                                            general_task_id = general_task,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = message,
                                            additional_data = additional_data
                                                )
    db_session.add(new_loan_case_history)
    
    
    
    
    commit_object(db_session)
    
    return {"OK"}








def check_if_exists(monitoring_case_id, db_session):#used
    get_cheduled_monitoring = db_session.query(ScheduledMonitoring).filter(ScheduledMonitoring.monitoring_case_id == monitoring_case_id).first()
    is_empty(get_cheduled_monitoring, 400, 'Scheduled monitoring has appointed already.')
    
    
    
    


def upload_file_send_scheduled_results(request, file_path,db_session):
    data = UpdateTaskManagerSendToCheck()
    data.task_manager_id = request.task_manager_id
    data.task_status = task_status['на проверку']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    
    scheduled = db_session.query(ScheduledMonitoring).filter(ScheduledMonitoring.id == request.scheduled_monitoring_id).first()
    
    if scheduled.deadline < datetime.datetime.now().date() and scheduled.scheduled_monitoring_result_id == None:
        get_expiration = db_session.query(ScheduledMonitoringExpiration).filter(ScheduledMonitoringExpiration.scheduled_monitoring_id == scheduled.id).first()
        if get_expiration is not None:
            get_expiration.due_date = datetime.datetime.now()
            get_expiration.updated_at = datetime.datetime.now()
        else:
        
            new_expiration = ScheduledMonitoringExpiration(scheduled_monitoring_id = scheduled.id,
                                                        responsible_id = request.from_user,
                                                        deadline_date = scheduled.deadline,
                                                        due_date = datetime.datetime.now(),
                                                        created_at = datetime.datetime.now()
                                                        )
        
            db_session.add(new_expiration)
    
    
    scheduled.scheduled_monitoring_status_id = monitoring_status['на проверку']
    if request.scheduled_monitoring_result_id is not None:
        scheduled.scheduled_monitoring_result_id = request.scheduled_monitoring_result_id
        if request.scheduled_monitoring_result_reason_other is not None:
            scheduled.scheduled_monitoring_result_reason_comment = request.scheduled_monitoring_result_reason_other
        
        elif request.scheduled_monitoring_result_reason is not None:
            scheduled.scheduled_monitoring_result_reason_id = request.scheduled_monitoring_result_reason
            
        scheduled.second_responsible_due_date = datetime.datetime.now()
        info_logger.info("user %s required 'upload_file_send_scheduled_results' method", request.from_user)
        info_logger.info("user %s sent files: %s", request.from_user, file_path)
    else:
        info_logger.info("user %s repeatedly requested upload_file_send_scheduled_results method", request.from_user)
        info_logger.info("user %s sent files: %s", request.from_user, file_path)                
    if request.project_status_id is not None:
        scheduled.project_status_id = request.project_status_id
    if request.amount is not None:
        scheduled.amount = request.amount
    
    scheduled.updated_at = datetime.datetime.now()
    scheduled.monitoring_case.loan_case[0].updated_at = datetime.datetime.now()
    
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == request.loan_case_id).first()
    data = CreateNotification()
    data.from_user_id = scheduled.monitoring_case.loan_case[0].main_responsible_id
    data.to_user_id = scheduled.monitoring_case.loan_case[0].main_responsible_id
    data.notification_type = notification_type['target_monitoring']
    data.body = notification_body['send_to_check']
    data.url = f'{get_loan_case.loan_portfolio_id}' + ':' + f'{get_loan_case.id}'+ ':' +f'{MGT.PLAN_MONITORING.value}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    additional_data = {'files':file_path}
    new_scheduled_history = ScheduledMonitoringHistory(monitoring_case_id = scheduled.monitoring_case_id, 
                                            type_id = CASE_HISTORY.SCHEDULED.value,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = loan_case_history['scheduled_send_to_check'],
                                            additional_data = additional_data
                                                )
    db_session.add(new_scheduled_history)
    
    save_file.append_monitoring_files(scheduled, file_path, db_session)
    commit_object(db_session)
    
    return "OK"



def upload_file_send_scheduled_resultsv2(request, file_path,db_session):
    data = UpdateTaskManagerSendToCheck()
    data.task_manager_id = request.task_manager_id
    data.task_status = task_status['на проверку']
    task = TaskManager_class(data)
    updated_task = task.update_task_manager(db_session)
    
    scheduled = db_session.query(ScheduledMonitoring).filter(ScheduledMonitoring.id == request.scheduled_monitoring_id).first()
    scheduled.scheduled_monitoring_status_id = monitoring_status['на проверку']
    scheduled.updated_at = datetime.datetime.now()
    
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == request.loan_case_id).first()
    data = CreateNotification()
    data.from_user_id = scheduled.monitoring_case.loan_case[0].main_responsible_id
    data.to_user_id = scheduled.monitoring_case.loan_case[0].main_responsible_id
    data.notification_type = notification_type['target_monitoring']
    data.body = notification_body['send_to_check']
    data.url = f'{get_loan_case.loan_portfolio_id}' + ':' + f'{get_loan_case.id}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    additional_data = {'Плановый мониторинг статус': 'на проверку'}
    new_loan_case_history = LoanCaseHistory(loan_case_id = request.loan_case_id,
                                            type_id = CASE_HISTORY.LOAN_CASE.value,
                                            general_task_id = updated_task.general_task_id,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = loan_case_history['scheduled_send_to_check'],
                                            additional_data = additional_data
                                                )
    db_session.add(new_loan_case_history)
    for path in file_path:
        new_file = MonitoringFiles(file_url = path, created_at = datetime.datetime.now())
        db_session.add(new_file)
        flush_object(db_session)
        
        scheduled.files.append(new_file)
        new_loan_case_history.files.append(new_file)
        db_session.add(new_loan_case_history)
        db_session.add(scheduled)
    
    
    commit_object(db_session)
    
    return "OK"
    
    
    
def get_all_scheduled_monitoring(monitoring_id, db_session):
    scheduled = []
    get_scheduled_case = db_session.query(ScheduledMonitoring).filter(ScheduledMonitoring.monitoring_case_id == MonitoringCase.id)\
        .filter(LoanCase.monitoring_case_id == MonitoringCase.id).filter(LoanCase.monitoring_case_id == monitoring_id).order_by(ScheduledMonitoring.id.asc()).all()
    is_exists(get_scheduled_case, 400, 'Scheduled monitoring not found')
    
    for  schedul in get_scheduled_case:
        scheduled.append({'id': schedul.id,
                          'scheduled_monitoring_status': schedul.scheduled_monitoring_status_id and schedul.status or None,
                          'scheduled_monitoring_result': schedul.scheduled_monitoring_result_id and schedul.result or None,
                          'scheduled_monitoring_result_reason': schedul.scheduled_monitoring_result_reason_id and schedul.reason or None,
                          'project_status': schedul.project_status_id and schedul.project_status or None,
                          'frequency_period':schedul.frequency_period_id and schedul.frequency_period or None,
                          'created_at':schedul.created_at,
                          'deadline':schedul.deadline,
                          'updated_at':schedul.updated_at,
                          'task': schedul.task and TaskManager_class.get_task_manager_by_id(schedul.task, db_session) or None,
                          'files': schedul.files and files_crud.get_case_files(schedul)})
        
    return scheduled
        

def get_scheduled_monitoring_details(scheduled_monitoring, db_session):
    scheduled = []
    
    for schedule in scheduled_monitoring:
        schedul = db_session.query(ScheduledMonitoring).filter(ScheduledMonitoring.id == schedule.id).first()
        is_exists(schedul, 400, 'Monitoring Case not found')
        
        scheduled_tasks = schedul.task and TaskManager_class.get_task_managers_by_id(schedul.task, db_session)
        scheduled.append({'id': schedul.id,
                        'scheduled_monitoring_status_id': schedul.scheduled_monitoring_status_id and schedul.status or None,
                        'scheduled_monitoring_result_reason': schedul.scheduled_monitoring_result_reason_id and schedul.reason or None,
                        'frequency_period_id':schedul.frequency_period_id and schedul.frequency_period or None,
                        'project_status': schedul.project_status_id and schedul.project_status or None,
                        'created_at':schedul.created_at,
                        'updated_at':schedul.updated_at,
                        'tasks': scheduled_tasks
                        })
            
        return scheduled
    
    
def get_frequency_periods(db_session):
    frequency_periods = []
    periods = db_session.query(MonitoringFrequencyPeriod).order_by(MonitoringFrequencyPeriod.id.asc()).all()
    for period in periods:
        frequency_periods.append({'id': period.id,
                        'name': period.name,
                        })
            
    return frequency_periods



def check_scheduled_monitoring(db_session):
    get_scheduled_monitoring  = db_session.query(ScheduledMonitoring)\
        .filter(ScheduledMonitoring.scheduled_monitoring_status_id ==monitoring_status['принят']).all()
    today = datetime.datetime.now().date()
    for schedule in get_scheduled_monitoring:
        if schedule.deadline ==  today:
            result  = get_frequency_period_by_date(schedule.frequency_period_id, db_session)
            new_scheduled_monitoring = ScheduledMonitoring(monitoring_case_id = schedule.monitoring_case_id,
                                             scheduled_monitoring_status_id = monitoring_status['назначен'],
                                             frequency_period_id = schedule.frequency_period_id,
                                             created_at = result['created_at'],
                                             deadline = result['deadline'])
            schedule.scheduled_monitoring_status_id = monitoring_status['завершено']
            db_session.add(new_scheduled_monitoring)
    commit_object(db_session)
    
    
    
def get_last_scheduled(monitoring_case_id, db_session,  status=None):
    get_scheduled  = db_session.query(ScheduledMonitoring).filter(ScheduledMonitoring.monitoring_case_id == monitoring_case_id)
    
    
    if status is not None:
        get_scheduled = get_scheduled.filter(ScheduledMonitoring.scheduled_monitoring_status_id==status)
    
    get_scheduled = get_scheduled.order_by(ScheduledMonitoring.id.desc()).first()
    
    if get_scheduled is not None:
        return get_scheduled
    return None