import datetime

from app.models.monitoring_case.reslut_reason_model import ResultReason
from app.models.statuses.monitoring_frequency_period_model import MonitoringFrequencyPeriod
from .....models.files.monitoring_files_model import MonitoringFiles
from .....models.monitoring_case.monitoring_case_model import MonitoringCase
from .....models.loan_case.loan_case_model import LoanCase
from .....models.loan_case.loan_case_history_model import LoanCaseHistory
from .....models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_model import UnscheduledMonitoring, unscheduled_monitoring_files
from .....models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_history import UnscheduledMonitoringHistory
from .....models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_expiration_model import UnscheduledMonitoringExpiration
from .....models.statuses.monitoring_frequency_period_model import MonitoringFrequencyPeriod
from .....common.is_empty import is_empty, is_exists
from .....common.commit import commit_object, flush_object
from ..script_date_holidays import get_business_days
from .....common import save_file
from dateutil.relativedelta import relativedelta
from .....schemas.juridical_case_schemas import SendToProblemAfterTarget
from ...juridical_case import juridical_case_crud
from ....monitoring_files import files_crud
from ...task_manager.task_manager_crud import TaskManager_class
from .....common.dictionaries.monitoring_case_dictionary import  monitoring_status
from .....common.dictionaries.notification_dictionary import notification_type, notification_body
from .....common.dictionaries.case_history_dictionaries import loan_case_history
from .....common.dictionaries.task_status_dictionaries import task_status
from .....schemas.task_manager_schemas import CreateTaskManagerSetTargetMonitoring,UpdateTaskManagerSendToCheck, UpdateTaskManagerAccept, GetaskManager,UpdateTaskManagerClose
from ...notification.notification_crud import Notificaton_class
from .....schemas.notification_schemas import CreateNotification
from .....config.logs_config import info_logger
import os
from ...problems_case import non_targeted_case
from .....common.dictionaries.general_tasks_dictionary import JGT, MGT, MAIN_DUE_DATE, CASE_HISTORY, DEADLINE_EXT


def appoint_unscheduled_monitoring(request, db_session):
    info_logger.info("user %s required 'appoint_unscheduled_monitoring' method", request.main_responsible_id)
    #check_if_exists(request.monitoring_case_id, db_session)
    data = CreateTaskManagerSetTargetMonitoring()
    data.general_task_id = MGT.UNSCHEDULED.value
    task = TaskManager_class(data)
    new_task = task.create_task_manager_when_set_scheduled_monitoring(db_session)
    
    new_unscheduled_monitoring = UnscheduledMonitoring(monitoring_case_id = request.monitoring_case_id,
                                             unscheduled_monitoring_status_id = monitoring_status['назначен'],
                                             task_manager_id  = new_task.id,
                                             created_at = datetime.datetime.now().date(),
                                             deadline = request.deadline)
    
    db_session.add(new_unscheduled_monitoring)
    flush_object(db_session)
    
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == request.loan_case_id).first()
    # data = UpdateTaskManagerAccept()
    # data.task_manager_id = get_loan_case.task_manager_id
    # data.general_task_id = MGT.UNSCHEDULED.value
    # data.task_status = task_status['завершено'],
    # task = TaskManager_class(data)
    # task.update_task_manager(db_session) 
    
    data = CreateNotification()
    data.from_user_id = request.main_responsible_id
    data.to_user_id = request.second_responsible_id
    data.notification_type = notification_type['unscheduled_monitoring']
    data.body = notification_body['appoint_unscheduled_monitoring']
    data.url = f'{get_loan_case.loan_portfolio_id}' + ':' + f'{get_loan_case.id}'+ ':' +f'{MGT.UNSCHEDULED.value}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    get_loan_case.updated_at = datetime.datetime.now()
    
    new_unscheduled_history = UnscheduledMonitoringHistory(monitoring_case_id = new_unscheduled_monitoring.monitoring_case_id, 
                                            type_id = CASE_HISTORY.UNSCHEDULED.value,
                                            from_user_id = request.main_responsible_id, 
                                            to_user_id= request.second_responsible_id,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = loan_case_history['appoint_unscheduled']
                                                )
    db_session.add(new_unscheduled_history)
    commit_object(db_session)
    
    return {"OK"}



def upload_file_send_unscheduled_results(request, file_path,db_session):
    # data = UpdateTaskManagerSendToCheck()
    # data.task_manager_id = request.task_manager_id
    # data.task_status = task_status['на проверку']
    # task = TaskManager_class(data)
    # task.update_task_manager(db_session)
    
    unscheduled = db_session.query(UnscheduledMonitoring).filter(UnscheduledMonitoring.id == request.unscheduled_monitoring_id).first()
    
    if unscheduled.deadline < datetime.datetime.now().date() and unscheduled.unscheduled_monitoring_result_id == None:
        get_expiration = db_session.query(UnscheduledMonitoringExpiration).filter(UnscheduledMonitoringExpiration.unscheduled_monitoring_id == unscheduled.id).first()
        if get_expiration is not None:
            get_expiration.due_date = datetime.datetime.now()
            get_expiration.updated_at = datetime.datetime.now()
        else:
        
            new_expiration = UnscheduledMonitoringExpiration(unscheduled_monitoring_id = unscheduled.id,
                                                        responsible_id = request.from_user,
                                                        deadline_date = unscheduled.deadline,
                                                        due_date = datetime.datetime.now(),
                                                        created_at = datetime.datetime.now()
                                                        )
        
            db_session.add(new_expiration)
    
    
    unscheduled.unscheduled_monitoring_status_id = monitoring_status['на проверку']
    if request.unscheduled_monitoring_result_id is not None:
        unscheduled.unscheduled_monitoring_result_id = request.unscheduled_monitoring_result_id
        
        if request.unscheduled_monitoring_result_reason_other is not None:
            unscheduled.unscheduled_monitoring_result_reason_comment = request.unscheduled_monitoring_result_reason_other
        
        elif request.unscheduled_monitoring_result_reason is not None:
            unscheduled.unscheduled_monitoring_result_reason_id = request.unscheduled_monitoring_result_reason
            
        unscheduled.second_responsible_due_date = datetime.datetime.now()
        info_logger.info("user %s required 'upload_file_send_unscheduled_results' method", request.from_user)
        info_logger.info("user %s sent files: %s", request.from_user, file_path)
    else:
        info_logger.info("user %s repeatedly requested upload_file_send_unscheduled_results method", request.from_user)
        info_logger.info("user %s sent files: %s", request.from_user, file_path)   
    if request.project_status_id is not None:
        unscheduled.project_status_id = request.project_status_id
    if request.amount is not None:
        unscheduled.amount = request.amount
   
    unscheduled.updated_at = datetime.datetime.now()
    unscheduled.monitoring_case.loan_case[0].updated_at = datetime.datetime.now()
    
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == request.loan_case_id).first()
    data = CreateNotification()
    data.from_user_id = unscheduled.monitoring_case.loan_case[0].main_responsible_id
    data.to_user_id = unscheduled.monitoring_case.loan_case[0].main_responsible_id
    data.notification_type = notification_type['unscheduled_monitoring']
    data.body = notification_body['send_to_check']
    data.url = f'{get_loan_case.loan_portfolio_id}' + ':' + f'{get_loan_case.id}'+ ':' +f'{MGT.UNSCHEDULED.value}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    additional_data = {'files':file_path}
    new_scheduled_history = UnscheduledMonitoringHistory(monitoring_case_id = unscheduled.monitoring_case_id, 
                                            type_id = CASE_HISTORY.UNSCHEDULED.value,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = loan_case_history['unscheduled_send_to_check'],
                                            additional_data = additional_data
                                                )
    db_session.add(new_scheduled_history)
    
    save_file.append_monitoring_files(unscheduled, file_path, db_session)
    commit_object(db_session)
    
    return "OK"











def accept_or_rework_unscheduled_monitoring(request, db_session):
    info_logger.info("user %s required 'accept__or_rework_unscheduled_monitoring' method", request.from_user)
    unscheduled = db_session.query(UnscheduledMonitoring).filter(UnscheduledMonitoring.id == request.unscheduled_monitoring_id).first()
    
    data = GetaskManager()
    data.task_manager_id = request.task_manager_id
    task = TaskManager_class(data)
    # get_task = task.get_task_by_id(db_session)
    # general_task = get_task.general_task_id
    
    if request.result_type:
        if unscheduled.unscheduled_monitoring_result_id == 2 or unscheduled.unscheduled_monitoring_result_id == 3:
            
            problem_data = SendToProblemAfterTarget()
            problem_data.general_task_id = MGT.SEND_JURIDIC.value
            problem_data.case_id = unscheduled.monitoring_case.loan_case[0].id
            problem_data.intended_overdue_type_id = unscheduled.unscheduled_monitoring_result_id
            problem_data.amount = unscheduled.amount
            problem_data.loan_portfolio_id = unscheduled.monitoring_case.loan_case[0].portfolio.id
            problem_data.local_code_id = unscheduled.monitoring_case.loan_case[0].portfolio.local_code_id
            problem_data.comment = request.comment and request.comment
            problem_data.from_user = request.from_user
            info_logger.info("user %s required sent unscheduled_monitoring to juridic", request.from_user)
            non_targeted_case.create_problems_non_target(problem_data, unscheduled.monitoring_case.loan_case[0].main_responsible.depart.id, unscheduled.files, db_session)
            
        else:
            data = UpdateTaskManagerAccept()
            data.task_manager_id = unscheduled.monitoring_case.loan_case[0].task_manager_id
            
            
        status = monitoring_status['проверено']
        message = loan_case_history['accepted_unscheduled']
        body = notification_body['accept_unscheduled_monitoring']
        data = UpdateTaskManagerAccept()
        data.task_manager_id = request.task_manager_id
        data.task_status = task_status['принят_ответственным']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
        unscheduled.monitoring_case.loan_case[0].updated_at = datetime.datetime.now()
        unscheduled.monitoring_case.loan_case[0].unscheduled_deadline_extension_status_id = DEADLINE_EXT.OK.value
        
        new_loan_case_history = UnscheduledMonitoringHistory(monitoring_case_id = unscheduled.monitoring_case_id, 
                                            type_id = CASE_HISTORY.UNSCHEDULED.value,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = message
                                                )
        db_session.add(new_loan_case_history)
        
    else:
        status = monitoring_status['переделать']
        message = loan_case_history['rejected_unscheduled']
        body = notification_body['rework_unscheduled_monitoring']
        data = UpdateTaskManagerAccept()
        data.task_manager_id = request.task_manager_id
        data.task_status = task_status['переделать']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
        file_path = files_crud.set_wrong_files(request.wrong_files, unscheduled, db_session)
        flush_object(db_session)
        info_logger.info("user %s sent unscheduled_monitoring to rework", request.from_user)
        info_logger.info("user %s sent to rework files: %s", request.from_user, file_path)
        new_loan_case_history = UnscheduledMonitoringHistory(monitoring_case_id = unscheduled.monitoring_case_id, 
                                            type_id = CASE_HISTORY.UNSCHEDULED.value,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = message
                                                )
    db_session.add(new_loan_case_history)
        
    unscheduled.unscheduled_monitoring_status_id = status
    unscheduled.main_responsible_due_date = datetime.datetime.now()
    
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == request.loan_case_id).first()
    #if unscheduled.unscheduled_monitoring_result_id != None and (datetime.datetime.now().date() - unscheduled.second_responsible_due_date.date()).days > MAIN_DUE_DATE.DATE.value:
    if unscheduled.unscheduled_monitoring_result_id != None and (get_business_days(datetime.datetime.now().date(), MAIN_DUE_DATE.DATE.value, db_session) - unscheduled.second_responsible_due_date.date()).days > 0:
        
        new_expiration = UnscheduledMonitoringExpiration(unscheduled_monitoring_id = unscheduled.id,
                                                    responsible_id = request.from_user,
                                                    deadline_date = unscheduled.deadline,
                                                    due_date = datetime.datetime.now(),
                                                    created_at = datetime.datetime.now())
    
        db_session.add(new_expiration)
    
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == request.loan_case_id).first()
   
    
    data = CreateNotification()
    data.from_user_id = request.from_user 
    data.to_user_id =request.to_user
    data.notification_type = notification_type['unscheduled_monitoring']
    data.body = body
    data.url = f'{get_loan_case.loan_portfolio_id}' + ':' + f'{get_loan_case.id}'+ ':' +f'{MGT.UNSCHEDULED.value}'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    
    
    commit_object(db_session)
    
    return "OK"








def get_all_unscheduled_monitoring(monitoring_id, db_session):
    unscheduled = []
    get_unscheduled_case = db_session.query(UnscheduledMonitoring).filter(UnscheduledMonitoring.monitoring_case_id == MonitoringCase.id)\
        .filter(LoanCase.monitoring_case_id == MonitoringCase.id).filter(LoanCase.monitoring_case_id == monitoring_id).order_by(UnscheduledMonitoring.id.asc()).all()
    is_exists(get_unscheduled_case, 400, 'Scheduled monitoring not found')
    
    for  unschedul in get_unscheduled_case:
        unscheduled.append({'id': unschedul.id,
                          'unscheduled_monitoring_status': unschedul.unscheduled_monitoring_status_id and unschedul.status or None,
                          'unscheduled_monitoring_result': unschedul.unscheduled_monitoring_result_id and unschedul.result or None,
                          'unscheduled_monitoring_result_reason': unschedul.unscheduled_monitoring_result_reason_id and unschedul.reason or None,
                          'created_at':unschedul.created_at,
                          'deadline':unschedul.deadline,
                          'updated_at':unschedul.updated_at,
                          'task': unschedul.task and TaskManager_class.get_task_manager_by_id(unschedul.task, db_session) or None,
                          'files': unschedul.files and files_crud.get_case_files(unschedul)})
        
    return unscheduled
        

def get_unscheduled_monitoring_details(unscheduled_monitoring, db_session):
    unscheduled = []
    
    for unschedule in unscheduled_monitoring:
        unschedul = db_session.query(UnscheduledMonitoring).filter(UnscheduledMonitoring.id == unschedule.id).first()
        is_exists(unschedul, 400, 'Unscheduled monitoring not found')
        
        unscheduled_tasks = unschedul.task and TaskManager_class.get_task_managers_by_id(unschedul.task, db_session)
        unscheduled.append({'id': unschedul.id,
                        'unscheduled_monitoring_status_id': unschedul.scheduled_monitoring_status_id and unschedul.status or None,
                        'unscheduled_monitoring_result': unschedul.unscheduled_monitoring_result_id and unschedul.result or None,
                        'unscheduled_monitoring_result_reason': unschedul.unscheduled_monitoring_result_reason_id and unschedul.reason or None,
                        'frequency_period_id':unschedul.frequency_period_id and unschedul.frequency_period or None,
                        'created_at':unschedul.created_at,
                        'updated_at':unschedul.updated_at,
                        'tasks': unscheduled_tasks
                        })
            
        return unscheduled




def get_last_unscheduled(monitoring_case_id, db_session):
    get_unscheduled  = db_session.query(UnscheduledMonitoring).filter(UnscheduledMonitoring.monitoring_case_id == monitoring_case_id).order_by(UnscheduledMonitoring.id.desc()).first()
    
    if get_unscheduled is not None:
        return get_unscheduled
    return None






def check_if_exists(monitoring_case_id, db_session):#used
    get_cheduled_monitoring = db_session.query(UnscheduledMonitoring).filter(UnscheduledMonitoring.monitoring_case_id == monitoring_case_id).first()
    is_empty(get_cheduled_monitoring, 400, 'Unscheduled monitoring has appointed already.')
    
    
    
    