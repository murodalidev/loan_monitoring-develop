from datetime import datetime

from app.models.loan_case.loan_case_model import LoanCase
from app.models.monitoring_case.monitoring_case_model import MonitoringCase
from app.models.monitoring_case.reslut_reason_model import ResultReason
from ....models.files.monitoring_files_model import MonitoringFiles
from ....models.loan_case.loan_case_history_model import LoanCaseHistory
from ....models.monitoring_case.target_monitoring_expiration_model import TargetMonitoringExpiration
from ....models.monitoring_case.target_monitoring_history_model import TargetMonitoringHistory
from ....models.monitoring_case.target_monitoring_model import TargetMonitoring
from ....models.statuses.target_monitoring_result_model import TargetMonitoringResult
from ....common.is_empty import is_exists
from ....common import save_file
from ....common.commit import commit_object, flush_object
from ..task_manager.task_manager_crud import TaskManager_class
from .script_date_holidays import get_business_days
from ....config.logs_config import info_logger
from ....common.dictionaries.monitoring_case_dictionary import  monitoring_status
from ....common.dictionaries.task_status_dictionaries import task_status
from ....common.dictionaries.case_history_dictionaries import loan_case_history
from ....common.dictionaries.notification_dictionary import notification_type, notification_body, notification_url
from ....schemas.task_manager_schemas import CreateTaskManagerSetTargetMonitoring, GetaskManager, UpdateTaskManagerSendToCheck, UpdateTaskManagerAccept, UpdateTaskManagerClose
from ..notification.notification_crud import Notificaton_class
from ....schemas.notification_schemas import CreateNotification
from ....schemas.juridical_case_schemas import SendToJuridicAfterTarget, SendToProblemAfterTarget
from . import monitoring_case_crud
from ....services.monitoring_files import files_crud
from ..juridical_case import juridical_case_crud
from ..problems_case import non_targeted_case
from sqlalchemy import or_
import os
from ....common.dictionaries.departments_dictionary import DEP
from ....common.dictionaries.general_tasks_dictionary import JGT, MGT, PGT, GTCAT, MAIN_DUE_DATE, CASE_HISTORY, DEADLINE_EXT


def appoint_target_monitoring(request, db_session):
    monitoring = monitoring_case_crud.check_if_empty(request.monitoring_case_id, db_session)
    
    data = CreateTaskManagerSetTargetMonitoring()
    data.general_task_id = request.general_task_id
    data.deadline = request.deadline
    task = TaskManager_class(data)
    new_task = task.create_task_manager_when_set_target_monitoring(db_session)
    
    
    new_target_monitoring = TargetMonitoring(target_monitoring_status_id = monitoring_status['назначен'],
                                             task_manager_id = new_task.id,
                                             deadline = request.deadline,
                                             created_at = datetime.now())
    
    db_session.add(new_target_monitoring)
    flush_object(db_session)
    
    data = UpdateTaskManagerClose()
    data.task_manager_id = monitoring.loan_case[0].task_manager_id
    data.general_task_id = request.general_task_id
    data.task_status = task_status['завершено']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    
    
    
    
    monitoring_case = monitoring_case_crud.set_target_monitoring(request.monitoring_case_id, new_target_monitoring.id, db_session)
    
    
    data = CreateNotification()
    data.from_user_id = request.main_responsible_id
    data.to_user_id = request.second_responsible_id
    data.notification_type = notification_type['target_monitoring']
    data.body = notification_body['appoint_target_monitoring']
    data.url = f'{monitoring.loan_case[0].loan_portfolio_id }' + ':' + f'{monitoring.loan_case[0].id}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    
    new_loan_case_history = LoanCaseHistory(loan_case_id = monitoring_case.loan_case[0].id,
                                            type_id = CASE_HISTORY.LOAN_CASE.value,
                                            general_task_id = request.general_task_id,
                                            from_user_id = request.main_responsible_id, 
                                            to_user_id= request.second_responsible_id,
                                            comment = request.comment,
                                            created_at = datetime.now(),
                                            message = loan_case_history['appoint_target']
                                                )
    db_session.add(new_loan_case_history)
    
    commit_object(db_session)
    
    return {"OK"}



def appoint_target_monitoringv2(request, db_session):
    monitoring = monitoring_case_crud.check_if_empty(request.monitoring_case_id, db_session)
    
    new_target_monitoring = TargetMonitoring(target_monitoring_status_id = monitoring_status['назначен'],
                                             deadline = request.deadline,
                                             created_at = datetime.now())
    
    db_session.add(new_target_monitoring)
    flush_object(db_session)
    
    data = UpdateTaskManagerClose()
    data.task_manager_id = monitoring.loan_case[0].task_manager_id
    data.general_task_id = request.general_task_id
    data.task_status = task_status['начато']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    
    monitoring_case = monitoring_case_crud.set_target_monitoring(request.monitoring_case_id, new_target_monitoring.id, db_session)
    
    
    data = CreateNotification()
    data.from_user_id = request.main_responsible_id
    data.to_user_id = request.second_responsible_id
    data.notification_type = notification_type['target_monitoring']
    data.body = notification_body['appoint_target_monitoring']
    data.url = f'{monitoring.loan_case[0].loan_portfolio_id }' + ':' + f'{monitoring.loan_case[0].id}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    
    new_loan_case_history = LoanCaseHistory(loan_case_id = monitoring_case.loan_case[0].id,
                                            type_id = CASE_HISTORY.LOAN_CASE.value,
                                            general_task_id = request.general_task_id,
                                            from_user_id = request.main_responsible_id, 
                                            to_user_id= request.second_responsible_id,
                                            comment = request.comment,
                                            created_at = datetime.now(),
                                            message = loan_case_history['appoint_target']
                                                )
    db_session.add(new_loan_case_history)
    
    commit_object(db_session)
    
    return {"OK"}




def appoint_target_monitoring_list_tasks(monitoring_case, general_task_id, main_responsible_id, second_responsible_id, db_session):
    #monitoring = monitoring_case_crud.check_if_empty(monitoring_case, db_session)
    
    data = CreateTaskManagerSetTargetMonitoring()
    data.general_task_id = general_task_id
    task = TaskManager_class(data)
    new_task = task.create_task_manager_when_set_target_monitoring(db_session)
    
    new_target_monitoring = TargetMonitoring(target_monitoring_status_id = monitoring_status['назначен'],
                                             task_manager_id = new_task.id,
                                             deadline = get_business_days(datetime.now().date(), 30, db_session),
                                             created_at = datetime.now())
    
    db_session.add(new_target_monitoring)
    flush_object(db_session)
    
    data = UpdateTaskManagerClose()
    data.task_manager_id = monitoring_case.loan_case[0].task_manager_id
    data.general_task_id = general_task_id
    data.task_status = task_status['завершено']
    task = TaskManager_class(data)
    task.update_task_manager(db_session)
    
    
    monitoring_case.target_monitoring_id = new_target_monitoring.id
    monitoring_case.updated_at = datetime.now()
    monitoring_case.loan_case[0].updated_at = datetime.now()
    flush_object(db_session)
    new_loan_case_history = TargetMonitoringHistory(target_monitoring_id = new_target_monitoring.id, 
                                            type_id = CASE_HISTORY.TARGET.value,
                                            from_user_id = main_responsible_id, 
                                            to_user_id= second_responsible_id,
                                            created_at = datetime.now(),
                                            message = loan_case_history['appoint_target']
                                                )
    db_session.add(new_loan_case_history)
    
    return {"OK"}





def get_target_monitoring(target_id, db_session):
    target = check_if_empty(target_id, db_session)
    target_monitoring = {}
    
    target_task = target.task and TaskManager_class.get_task_managers_by_id(target.task, db_session)
    target_monitoring = {'id':target.id,
                        'target_monitoring_status': target.target_monitoring_status_id and target.status or None,
                        'target_monitoring_result': target.target_monitoring_result_id and target.result or None,
                        'target_monitoring_result_reason': target.target_monitoring_result_reason_id and target.reason or None,
                        'target_monitoring_result_reason_comment': target.target_monitoring_result_reason_comment and target.target_monitoring_result_reason_comment or None,
                        'main_responsible':target.monitoring_case[0].loan_case[0].main_responsible.full_name,
                        'second_responsible':target.monitoring_case[0].loan_case[0].second_responsible.full_name,
                        'deadline': target.deadline and target.deadline or None,
                        'main_responsible_due_date': target.main_responsible_due_date and target.main_responsible_due_date or None,
                        'second_responsible_due_date': target.second_responsible_due_date and target.second_responsible_due_date or None,
                        'amount': target.amount and target.amount or None,
                        'created_at': target.created_at and target.created_at or None,
                        'updated_at': target.updated_at and target.updated_at or None,
                        'task': target_task,
                        'files': target.files and files_crud.get_case_files(target) or None}
    
    return target_monitoring
    



def get_target_monitoring_for_problem(monitoring_case_id, db_session):
    target = db_session.query(TargetMonitoring).join(MonitoringCase, MonitoringCase.target_monitoring_id == TargetMonitoring.id).filter(MonitoringCase.id ==monitoring_case_id).first()
    #is_exists(target, 400, 'Target Monitoring not found')
    target_monitoring = {}
    if target is not None:
        target_task = target.task and TaskManager_class.get_task_managers_by_id(target.task, db_session)
        target_monitoring = {'id':target.id,
                            'target_monitoring_status': target.target_monitoring_status_id and target.status or None,
                            'target_monitoring_result': target.target_monitoring_result_id and target.result or None,
                            'target_monitoring_result_reason': target.target_monitoring_result_reason_id and target.reason or None,
                            'main_responsible':target.monitoring_case[0].loan_case[0].main_responsible.full_name,
                            'second_responsible':target.monitoring_case[0].loan_case[0].second_responsible.full_name,
                            'deadline': target.deadline and target.deadline or None,
                            'main_responsible_due_date': target.main_responsible_due_date and target.main_responsible_due_date or None,
                            'second_responsible_due_date': target.second_responsible_due_date and target.second_responsible_due_date or None,
                            'amount': target.amount and target.amount or None,
                            'created_at': target.created_at and target.created_at or None,
                            'updated_at': target.updated_at and target.updated_at or None,
                            'task': target_task,
                            'files': target.files and files_crud.get_case_files(target) or None}
    
    return target_monitoring





def accept__or_rework_target_monitoring(request, db_session):
    info_logger.info("user %s required 'accept_or_rework_target_monitoring' method", request.from_user)
    target = db_session.query(TargetMonitoring).filter(TargetMonitoring.id == request.target_monitoring_id).first()
    
    
    # data = GetaskManager()
    # data.task_manager_id = request.task_manager_id
    # task = TaskManager_class(data)
    # get_task = task.get_task_by_id(db_session)
    if request.result_type:
        if target.target_monitoring_result_id !=1:
            
            problem_data = SendToProblemAfterTarget()
            problem_data.general_task_id = MGT.SEND_PORBLEM.value
            problem_data.case_id = target.monitoring_case[0].loan_case[0].id
            problem_data.intended_overdue_type_id = target.target_monitoring_result_id
            problem_data.amount = target.amount
            problem_data.loan_portfolio_id = target.monitoring_case[0].loan_case[0].portfolio.id
            problem_data.local_code_id = target.monitoring_case[0].loan_case[0].portfolio.local_code_id
            problem_data.comment = request.comment and request.comment
            problem_data.from_user = request.from_user
            
            non_targeted_case.create_problems_non_target(problem_data, target.monitoring_case[0].loan_case[0].main_responsible.depart.id, target.files, db_session)
            
        else:
            data = UpdateTaskManagerAccept()
            data.task_manager_id = target.monitoring_case[0].loan_case[0].task_manager_id
            data.general_task_id = MGT.PLAN_MONITORING.value
            data.task_status = task_status['начато'],
            task = TaskManager_class(data)
            task.update_task_manager(db_session)   
        target.monitoring_case[0].loan_case[0].target_deadline_extension_status_id = DEADLINE_EXT.OK.value
        status = monitoring_status['проверено']
        additional_data = {'target_monitoring_status': 'проверено'}
        message = loan_case_history['accepted']
        body = notification_body['accept_target_monitoring']
        data = UpdateTaskManagerAccept()
        data.task_manager_id = request.task_manager_id
        data.task_status = task_status['принят_ответственным']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
        info_logger.info("user %s accepted target monitoring", request.from_user)
        
        
    else:
        status = monitoring_status['переделать']
        additional_data = {'target_monitoring_status': 'переделать'}
        message = loan_case_history['rejected']
        body = notification_body['rework_target_monitoring']
        data = UpdateTaskManagerAccept()
        data.task_manager_id = request.task_manager_id
        data.task_status = task_status['переделать']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
        file_path = files_crud.set_wrong_files(request.wrong_files, target, db_session)
        info_logger.info("user %s sent to rework target monitoring", request.from_user)
        info_logger.info("user %s sent to rework files: %s", request.from_user, file_path)
        db_session.add(target)
    target.target_monitoring_status_id = status
    if target.main_responsible_due_date is None:
        target.main_responsible_due_date = datetime.now()
    target.monitoring_case[0].loan_case[0].updated_at = datetime.now()
    #if target.target_monitoring_result_id != None and (datetime.now().date() - target.second_responsible_due_date.date()).days > MAIN_DUE_DATE.DATE.value:
    
    if target.target_monitoring_result_id != None and (get_business_days(datetime.now().date(), MAIN_DUE_DATE.DATE.value, db_session) - target.second_responsible_due_date.date()).days > 0:
        new_expiration = TargetMonitoringExpiration(target_monitoring_id = target.id,
                                                    responsible_id = request.from_user,
                                                    deadline_date = target.deadline,
                                                    due_date = datetime.now(),
                                                    created_at = datetime.now())
    
        db_session.add(new_expiration)
    
    
    data = CreateNotification()
    data.from_user_id = request.from_user 
    data.to_user_id =request.to_user
    data.notification_type = notification_type['target_monitoring']
    data.body = body
    data.url = f'{target.monitoring_case[0].loan_case[0].loan_portfolio_id}' + ':' + f'{target.monitoring_case[0].loan_case[0].id}' + ':' +f'{MGT.TARGET_MONITORING.value}'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    new_target_history = TargetMonitoringHistory(target_monitoring_id = target.id, 
                                            type_id = CASE_HISTORY.TARGET.value,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.now(),
                                            message = message,
                                            additional_data = additional_data
                                                )
    db_session.add(new_target_history)
    
    
    
    commit_object(db_session)
    
    return {"OK"}




def accept__or_rework_target_monitoringv2(request, db_session):
    target = db_session.query(TargetMonitoring).filter(TargetMonitoring.id == request.target_monitoring_id).first()
    data = GetaskManager()
    data.task_manager_id = request.task_manager_id
    task = TaskManager_class(data)
    get_task = task.get_task_by_id(db_session)
    
    if request.result_type:
        status = monitoring_status['проверено']
        additional_data = {'target_monitoring_status': 'проверено'}
        message = loan_case_history['accepted']
        body = notification_body['accept_target_monitoring']
        data = UpdateTaskManagerAccept()
        data.task_manager_id = request.task_manager_id
        task = TaskManager_class(data)
        task.loan_case_task_manager_set_on_work(db_session)
        
    else:
        status = monitoring_status['переделать']
        additional_data = {'target_monitoring_status': 'переделать'}
        message = loan_case_history['rejected']
        body = notification_body['rework_target_monitoring']
        data = UpdateTaskManagerAccept()
        data.task_manager_id = request.task_manager_id
        data.task_status = task_status['переделать']
        task = TaskManager_class(data)
        task.update_task_manager(db_session)
        target.files.clear()
        db_session.add(target)
    target.target_monitoring_status_id = status
    
    
    
    data = CreateNotification()
    data.from_user_id = request.from_user 
    data.to_user_id =request.to_user
    data.notification_type = notification_type['target_monitoring']
    data.body = body
    data.url = f'{target.monitoring_case[0].loan_case[0].loan_portfolio_id}' + ':' + f'{target.monitoring_case[0].loan_case[0].id}'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    new_loan_case_history = LoanCaseHistory(loan_case_id = request.loan_case_id, 
                                            general_task_id = get_task.general_task_id,
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







    
def check_if_empty(target_id, db_session):#used
    target = db_session.query(TargetMonitoring).filter(TargetMonitoring.id ==target_id).first()
    is_exists(target, 400, 'Target Monitoring not found')
    return target
    
    


    
def upload_file_send_target_results(request, file_path, db_session):
    data = UpdateTaskManagerSendToCheck()
    data.task_manager_id = request.task_manager_id
    data.task_status = task_status['на проверку']
    task = TaskManager_class(data)
    updated_task = task.update_task_manager(db_session)
    
    
    target = db_session.query(TargetMonitoring).filter(TargetMonitoring.id == request.target_monitoring_id).first()
    
    if target.deadline < datetime.now() and target.target_monitoring_result_id == None:
        
        get_expiration = db_session.query(TargetMonitoringExpiration).filter(TargetMonitoringExpiration.target_monitoring_id == target.id)\
            .filter(TargetMonitoringExpiration.due_date == None).first()
        
        if get_expiration is not None:
            get_expiration.due_date = datetime.now()
            get_expiration.updated_at = datetime.now()
        else:
            new_expiration = TargetMonitoringExpiration(target_monitoring_id = target.id,
                                                    responsible_id = request.from_user,
                                                    deadline_date = target.deadline,
                                                    due_date = datetime.now(),
                                                    created_at = datetime.now()
                                                    )
    
            db_session.add(new_expiration)
    
    target.target_monitoring_status_id = monitoring_status['на проверку']
    if request.target_monitoring_result is not None:
        info_logger.info("user %s required 'upload_file_send_target_results' method", request.from_user)
        info_logger.info("user %s sent files: %s", request.from_user, file_path)
        target.target_monitoring_result_id = request.target_monitoring_result
        if request.target_monitoring_result_reason_other is not None:
            target.target_monitoring_result_reason_comment = request.target_monitoring_result_reason_other
        
        elif request.target_monitoring_result_reason is not None:
            target.target_monitoring_result_reason_id = request.target_monitoring_result_reason
        target.second_responsible_due_date = datetime.now()
    else:
        info_logger.info("user %s repeatedly requested upload_file_send_target_results method", request.from_user)
        info_logger.info("user %s sent files: %s", request.from_user, file_path)
    target.monitoring_case[0].loan_case[0].updated_at = datetime.now()
    if request.amount is not None:
        target.amount = request.amount
    
    additional_data = {'files':file_path}
    
    data = CreateNotification()
    data.from_user_id = target.monitoring_case[0].loan_case[0].second_responsible_id
    data.to_user_id = target.monitoring_case[0].loan_case[0].main_responsible_id
    data.notification_type = notification_type['target_monitoring']
    data.body = notification_body['send_to_check']
    data.url = f'{target.monitoring_case[0].loan_case[0].loan_portfolio_id}' + ':' + f'{target.monitoring_case[0].loan_case[0].id}'+ ':' +f'{MGT.TARGET_MONITORING.value}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    new_target_history = TargetMonitoringHistory(target_monitoring_id = target.id, 
                                            type_id = CASE_HISTORY.TARGET.value,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.now(),
                                            message = loan_case_history['target_send_to_check'],
                                            additional_data = additional_data
                                                )
    db_session.add(new_target_history)
    save_file.append_monitoring_files(target, file_path, db_session)
    commit_object(db_session)
    
    return "OK"


def upload_file_send_target_resultsv2(request, file_path, db_session):
    data = UpdateTaskManagerSendToCheck()
    data.task_manager_id = request.task_manager_id
    data.task_status = task_status['на проверку']
    task = TaskManager_class(data)
    updated_task = task.update_task_manager(db_session)
    
    
    target = db_session.query(TargetMonitoring).filter(TargetMonitoring.id == request.target_monitoring_id).first()
    target.target_monitoring_status_id = monitoring_status['на проверку']
    target.target_monitoring_result_id = request.target_monitoring_result
    if request.target_monitoring_result_reason is not None:
            target.target_monitoring_result_reason_id = request.target_monitoring_result_reason
    target.amount = request.amount and request.amount or None
    
    additional_data = {'Мониторинг статуси': 'на проверку',
                       'amount': request.amount and request.amount or None,
                       'result':get_target_monitoring_result_by_id(request.target_monitoring_result, db_session)}
    
    data = CreateNotification()
    data.from_user_id = target.monitoring_case[0].loan_case[0].second_responsible_id
    data.to_user_id = target.monitoring_case[0].loan_case[0].main_responsible_id
    data.notification_type = notification_type['target_monitoring']
    data.body = notification_body['send_to_check']
    data.url = f'{target.monitoring_case[0].loan_case[0].loan_portfolio_id}' + ':' + f'{target.monitoring_case[0].loan_case[0].id}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    new_loan_case_history = LoanCaseHistory(loan_case_id = request.loan_case_id, 
                                            general_task_id = updated_task.general_task_id,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = loan_case_history['target_send_to_check'],
                                            additional_data = additional_data
                                                )
    db_session.add(new_loan_case_history)
    for file in file_path:
        new_file = MonitoringFiles(file_url = file, created_at = datetime.datetime.now())
        db_session.add(new_file)
        flush_object(db_session)
        new_loan_case_history.files.append(new_file)
        db_session.add(new_loan_case_history)
        target.files.append(new_file)
        db_session.add(target)
    commit_object(db_session)
    
    return "OK"








def get_target_monitoring_results(db_session):
    target_results = []
    results = db_session.query(TargetMonitoringResult).order_by(TargetMonitoringResult.id.asc()).all()
    for result in results:
        target_results.append({'id': result.id,
                        'name': result.name,
                        'code': result.code
                        })
            
    return target_results



def get_target_monitoring_result_by_id(id, db_session):#used
    result = db_session.query(TargetMonitoringResult).filter(TargetMonitoringResult.id == id).first()
    return result.name









def reset_target_monitoring(loan_case_id, db_session):
    target_monitoring = db_session.query(TargetMonitoring).join(MonitoringCase, MonitoringCase.target_monitoring_id == TargetMonitoring.id)\
        .join(LoanCase, LoanCase.monitoring_case_id == MonitoringCase.id)\
            .filter(LoanCase.id == loan_case_id).first()
    if target_monitoring is not None:
        if target_monitoring.files != []:
            f_list = [{"id":file.id,"type":file.ftype,"url": file.file_url, "is_correct": file.is_correct} for file in target_monitoring.files]
        
        for fil in f_list:
            try:
                os.remove(fil['url'])
            except:
                print('files not found')
            get_file = db_session.query(MonitoringFiles).filter(MonitoringFiles.id==fil["id"]).first()
            target_monitoring.files.remove(get_file)
            db_session.add(target_monitoring)
            db_session.delete(get_file)
            commit_object(db_session)
            
        target_monitoring.target_monitoring_status_id = 1
        target_monitoring.target_monitoring_result_id = None
        target_monitoring.target_monitoring_result_reason_id = None
        target_monitoring.target_monitoring_result_reason_comment = None
        target_monitoring.amount = None
        target_monitoring.main_responsible_due_date = None
        target_monitoring.second_responsible_due_date = None
        
        
        data = UpdateTaskManagerAccept()
        data.task_manager_id = target_monitoring.monitoring_case[0].loan_case[0].task_manager_id
        data.general_task_id = MGT.TARGET_MONITORING.value
        data.task_status = task_status['завершено'],
        task = TaskManager_class(data)
        task.update_task_manager(db_session) 
        
        
        get_history = db_session.query(TargetMonitoringHistory).filter(TargetMonitoringHistory.target_monitoring_id == target_monitoring.id).all()
        
        for history in get_history:
            db_session.delete(history)
            flush_object(db_session)
        commit_object(db_session)
        return "OK"
    else:
        return "Empty data"