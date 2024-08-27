from datetime import datetime, timedelta

from ....models.monitoring_case.scheduled_monitoring_expiration_model import ScheduledMonitoringExpiration
from ....models.monitoring_case.target_monitoring_expiration_model import TargetMonitoringExpiration
from ....models.files.monitoring_files_model import MonitoringFiles
from ....models.monitoring_case.monitoring_case_model import MonitoringCase
from ....models.loan_case.loan_case_model import LoanCase
from ....models.monitoring_task_manager.task_manager_model import TaskManager
from ....models.loan_case.loan_case_history_model import LoanCaseHistory
from ....models.monitoring_case.target_monitoring_model import TargetMonitoring
from ....models.monitoring_case.extension_history_model import TargetDeadlineExtensionMonitoringHistory, target_extension_files
from ....models.monitoring_case.extension_history_model import ScheduledDeadlineExtensionMonitoringHistory, scheduled_extension_files
from ....models.monitoring_case.extension_history_model import UnscheduledDeadlineExtensionMonitoringHistory, unscheduled_extension_files
from ....models.monitoring_case.scheduled_monitoring_model import ScheduledMonitoring
from ....models.statuses.case_history_type_model import CaseHistoryType
from ....models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_model import UnscheduledMonitoring
from ....models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_expiration_model import UnscheduledMonitoringExpiration
from ....models.statuses.target_monitoring_result_model import TargetMonitoringResult
from ....common.is_empty import is_empty, is_empty_list, is_exists
from ....common.commit import commit_object, flush_object
from ..task_manager.task_manager_crud import TaskManager_class
from  app.services.users.users_crud import Users as users
from ....schemas.task_manager_schemas import UpdateTaskManagerSetResponsible
from ....common.dictionaries.task_status_dictionaries import task_status
from ....common.dictionaries.case_history_dictionaries import loan_case_history
from ....common.dictionaries.notification_dictionary import notification_type, notification_body, notification_url
from ..notification.notification_crud import Notificaton_class
from ....schemas.notification_schemas import CreateNotification
from ....schemas.juridical_case_schemas import SendToJuridicAfterTarget
from . import monitoring_case_crud
from ....services.monitoring_files import files_crud
from ..juridical_case import juridical_case_crud
from sqlalchemy import or_
from ....common.dictionaries.departments_dictionary import DEP
from ....common.dictionaries.general_tasks_dictionary import JGT, MGT, PGT, GTCAT, CASE_HISTORY
from ....config.logs_config import info_logger

    
def request_extension(request, file_path, db_session):
    case_hist = None
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == request.loan_case_id).first()
    if request.case_type_id == CASE_HISTORY.TARGET.value:
        case_hist = CASE_HISTORY.TARGET.value
        get_loan_case.target_deadline_extension_status_id = 3
        get_loan_case.updated_at = datetime.now()
        flush_object(db_session)
        new_target_extension_history = TargetDeadlineExtensionMonitoringHistory(target_monitoring_id = get_loan_case.monitoring_case.target.id,
                                                from_user_id = get_loan_case.second_responsible_id, 
                                                to_user_id= get_loan_case.main_responsible_id,
                                                type_id=2,
                                                comment = request.comment,
                                                created_at = datetime.now(),
                                                message = loan_case_history['deadline_extension_request']
                                                    )
        db_session.add(new_target_extension_history)
        info_logger.info("user %s requested TARGET request_extension method", get_loan_case.second_responsible_id)
    
    elif request.case_type_id == CASE_HISTORY.SCHEDULED.value:
        case_hist = CASE_HISTORY.SCHEDULED.value 
        get_loan_case.scheduled_deadline_extension_status_id = 3
        get_loan_case.updated_at = datetime.now()
        flush_object(db_session)
        get_scheduled  = db_session.query(ScheduledMonitoring).filter(ScheduledMonitoring.monitoring_case_id == get_loan_case.monitoring_case_id).order_by(ScheduledMonitoring.id.desc()).first()
        new_target_extension_history = ScheduledDeadlineExtensionMonitoringHistory(scheduled_monitoring_id = get_scheduled.id,
                                                from_user_id = get_loan_case.second_responsible_id, 
                                                to_user_id= get_loan_case.main_responsible_id,
                                                type_id=2,
                                                comment = request.comment,
                                                created_at = datetime.now(),
                                                message = loan_case_history['deadline_extension_request']
                                                    )
        db_session.add(new_target_extension_history)
        info_logger.info("user %s requested SCHEDULED request_extension method", get_loan_case.second_responsible_id)
    
    elif request.case_type_id == CASE_HISTORY.UNSCHEDULED.value:
        case_hist = CASE_HISTORY.UNSCHEDULED.value   
        get_loan_case.unscheduled_deadline_extension_status_id = 3
        get_loan_case.updated_at = datetime.now()
        flush_object(db_session)
        get_unscheduled  = db_session.query(UnscheduledMonitoring).filter(UnscheduledMonitoring.monitoring_case_id == get_loan_case.monitoring_case_id).order_by(UnscheduledMonitoring.id.desc()).first()
        new_target_extension_history = UnscheduledDeadlineExtensionMonitoringHistory(unscheduled_monitoring_id = get_unscheduled.id,
                                                from_user_id = get_loan_case.second_responsible_id, 
                                                to_user_id= get_loan_case.main_responsible_id,
                                                type_id=2,
                                                comment = request.comment,
                                                created_at = datetime.now(),
                                                message = loan_case_history['deadline_extension_request']
                                                    )
        db_session.add(new_target_extension_history)
        info_logger.info("user %s requested UNSCHEDULED request_extension method", get_loan_case.second_responsible_id)
    
    
    data = CreateNotification()
    data.from_user_id = get_loan_case.second_responsible_id
    data.to_user_id = get_loan_case.main_responsible_id
    data.notification_type = notification_type['monitoring']
    data.body = notification_body['deadline_extension_request']
    data.url = f'{get_loan_case.loan_portfolio_id}:{get_loan_case.id}:{MGT.DEADLINE_EXTENSION.value}:{case_hist}'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    for file in file_path:
        new_file = MonitoringFiles(file_url = file['name'], created_at = datetime.now(),
                                   ftype = file['type_code'])
        db_session.add(new_file)
        flush_object(db_session)
        new_target_extension_history.files.append(new_file)
        db_session.add(new_target_extension_history)
    commit_object(db_session)
    info_logger.info("user %s sent files: %s", get_loan_case.second_responsible_id, file_path)
    
    return "OK"



def accept_or_decline_extension(request, db_session):
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == request.loan_case_id).first()
    if request.result:
        get_loan_case.updated_at = datetime.now()
        
        if request.case_type_id == CASE_HISTORY.TARGET.value:
            case_hist = CASE_HISTORY.TARGET.value 
            get_loan_case.target_deadline_extension_status_id = 1
            db_session.add(get_loan_case)
            get_target_monitoring = db_session.query(TargetMonitoring)\
                .filter(TargetMonitoring.id == MonitoringCase.target_monitoring_id)\
                .filter(MonitoringCase.id == get_loan_case.monitoring_case_id).first()
                
            get_target_monitoring.deadline = datetime.strptime(request.date, '%Y-%m-%d %H:%M')
            get_target_monitoring.updated_at = datetime.now()
            
            
            get_target_deadline = db_session.query(TargetMonitoringExpiration)\
            .filter(TargetMonitoringExpiration.target_monitoring_id == get_loan_case.monitoring_case.target.id)\
                .order_by(TargetMonitoringExpiration.id.desc()).first()
            db_session.delete(get_target_deadline)
            flush_object(db_session)
            
            new_loan_case_history = TargetDeadlineExtensionMonitoringHistory(target_monitoring_id = get_loan_case.monitoring_case.target.id,
                            to_user_id = get_loan_case.second_responsible_id, 
                            from_user_id= get_loan_case.main_responsible_id,
                            comment = request.comment,
                            created_at = datetime.now(),
                            message = loan_case_history['deadline_extension_accept'])
            db_session.add(new_loan_case_history)
            info_logger.info("user %s accepted TARGET deadline extension", get_loan_case.main_responsible_id)
            
        
        elif request.case_type_id == CASE_HISTORY.SCHEDULED.value:
            case_hist = CASE_HISTORY.SCHEDULED.value 
            get_loan_case.scheduled_deadline_extension_status_id = 1
            get_scheduled  = db_session.query(ScheduledMonitoring).filter(ScheduledMonitoring.monitoring_case_id == get_loan_case.monitoring_case_id).order_by(ScheduledMonitoring.id.desc()).first()
            
            get_scheduled.deadline = datetime.strptime(request.date, '%Y-%m-%d %H:%M').date()
            get_scheduled.updated_at = datetime.now()
            
            get_scheduled_deadline = db_session.query(ScheduledMonitoringExpiration)\
            .filter(ScheduledMonitoringExpiration.scheduled_monitoring_id == get_scheduled.id).order_by(ScheduledMonitoringExpiration.id.desc()).first()
            db_session.delete(get_scheduled_deadline)
            
            flush_object(db_session)
            get_scheduled  = db_session.query(ScheduledMonitoring).filter(ScheduledMonitoring.monitoring_case_id == get_loan_case.monitoring_case_id).order_by(ScheduledMonitoring.id.desc()).first()
            new_loan_case_history = ScheduledDeadlineExtensionMonitoringHistory(scheduled_monitoring_id = get_scheduled.id,
                                                to_user_id = get_loan_case.second_responsible_id, 
                                                from_user_id= get_loan_case.main_responsible_id,
                                                comment = request.comment,
                                                created_at = datetime.now(),
                                                message = loan_case_history['deadline_extension_accept']
                                                    )
            db_session.add(new_loan_case_history)
            info_logger.info("user %s accepted SCHEDULED deadline extension", get_loan_case.main_responsible_id)
            
            
        elif request.case_type_id == CASE_HISTORY.UNSCHEDULED.value:
            case_hist = CASE_HISTORY.UNSCHEDULED.value 
            get_loan_case.unscheduled_deadline_extension_status_id = 1
            get_unscheduled  = db_session.query(UnscheduledMonitoring).filter(UnscheduledMonitoring.monitoring_case_id == get_loan_case.monitoring_case_id).order_by(UnscheduledMonitoring.id.desc()).first()
           
            get_unscheduled.deadline = datetime.strptime(request.date, '%Y-%m-%d %H:%M').date()
            get_unscheduled.updated_at = datetime.now()
            get_unscheduled_deadline = db_session.query(UnscheduledMonitoringExpiration)\
            .filter(UnscheduledMonitoringExpiration.unscheduled_monitoring_id == get_unscheduled.id).order_by(UnscheduledMonitoringExpiration.id.desc()).first()
            db_session.delete(get_unscheduled_deadline)
            
            flush_object(db_session)
            get_unscheduled  = db_session.query(UnscheduledMonitoring).filter(UnscheduledMonitoring.monitoring_case_id == get_loan_case.monitoring_case_id).order_by(UnscheduledMonitoring.id.desc()).first()
            new_loan_case_history = UnscheduledDeadlineExtensionMonitoringHistory(unscheduled_monitoring_id = get_unscheduled.id,
                                                to_user_id = get_loan_case.second_responsible_id, 
                                                from_user_id= get_loan_case.main_responsible_id,
                                                comment = request.comment,
                                                created_at = datetime.now(),
                                                message = loan_case_history['deadline_extension_accept']
                                                    )
            db_session.add(new_loan_case_history)
            info_logger.info("user %s accepted UNSCHEDULED deadline extension", get_loan_case.main_responsible_id)
        
        data = CreateNotification()
        data.to_user_id = get_loan_case.second_responsible_id
        data.from_user_id = get_loan_case.main_responsible_id
        data.notification_type = notification_type['monitoring']
        data.body = notification_body['deadline_extension_accept']
        data.url = f'{get_loan_case.loan_portfolio_id}:{get_loan_case.id}:{MGT.DEADLINE_EXTENSION.value}:{case_hist}'
        
        notifiaction = Notificaton_class(data)
        notifiaction.create_notification(db_session)
        
    else:
        if request.case_type_id == CASE_HISTORY.TARGET.value:
            case_hist = CASE_HISTORY.TARGET.value 
            get_loan_case.target_deadline_extension_status_id = 2
            get_loan_case.updated_at = datetime.now()
            
            data = CreateNotification()
            data.to_user_id = get_loan_case.second_responsible_id
            data.from_user_id = get_loan_case.main_responsible_id
            data.notification_type = notification_type['monitoring']
            data.body = notification_body['deadline_extension_decline']
            data.url = f'{get_loan_case.loan_portfolio_id}' + ':' + f'{get_loan_case.id}'+ ':' +f'{MGT.DEADLINE_EXTENSION.value}:{case_hist}'
            
            notifiaction = Notificaton_class(data)
            notifiaction.create_notification(db_session)
            new_loan_case_history = TargetDeadlineExtensionMonitoringHistory(target_monitoring_id = get_loan_case.monitoring_case.target.id,
                                                    to_user_id = get_loan_case.second_responsible_id, 
                                                    from_user_id= get_loan_case.main_responsible_id,
                                                    comment = request.comment,
                                                    created_at = datetime.now(),
                                                    message = loan_case_history['deadline_extension_decline']
                                                        )
            db_session.add(new_loan_case_history)
            info_logger.info("user %s declined TARGET deadline extension", get_loan_case.main_responsible_id)
        elif request.case_type_id == CASE_HISTORY.SCHEDULED.value:
            case_hist = CASE_HISTORY.SCHEDULED.value 
            get_loan_case.scheduled_deadline_extension_status_id = 2
            get_loan_case.updated_at = datetime.now()
            
            data = CreateNotification()
            data.to_user_id = get_loan_case.second_responsible_id
            data.from_user_id = get_loan_case.main_responsible_id
            data.notification_type = notification_type['monitoring']
            data.body = notification_body['deadline_extension_decline']
            data.url = f'{get_loan_case.loan_portfolio_id}:{get_loan_case.id}:{MGT.DEADLINE_EXTENSION.value}:{case_hist}'
            
            notifiaction = Notificaton_class(data)
            notifiaction.create_notification(db_session)
            get_scheduled  = db_session.query(ScheduledMonitoring).filter(ScheduledMonitoring.monitoring_case_id == get_loan_case.monitoring_case_id).order_by(ScheduledMonitoring.id.desc()).first()
            new_loan_case_history = ScheduledDeadlineExtensionMonitoringHistory(scheduled_monitoring_id = get_scheduled.id,
                                                    to_user_id = get_loan_case.second_responsible_id, 
                                                    from_user_id= get_loan_case.main_responsible_id,
                                                    comment = request.comment,
                                                    created_at = datetime.now(),
                                                    message = loan_case_history['deadline_extension_decline']
                                                        )
            db_session.add(new_loan_case_history)
            info_logger.info("user %s declined SCHEDULED deadline extension", get_loan_case.main_responsible_id)
        elif request.case_type_id == CASE_HISTORY.UNSCHEDULED.value:
            case_hist = CASE_HISTORY.UNSCHEDULED.value 
            get_loan_case.unscheduled_deadline_extension_status_id = 2
            get_loan_case.updated_at = datetime.now()
            
            data = CreateNotification()
            data.to_user_id = get_loan_case.second_responsible_id
            data.from_user_id = get_loan_case.main_responsible_id
            data.notification_type = notification_type['monitoring']
            data.body = notification_body['deadline_extension_decline']
            data.url = f'{get_loan_case.loan_portfolio_id}:{get_loan_case.id}:{MGT.DEADLINE_EXTENSION.value}:{case_hist}'
            
            notifiaction = Notificaton_class(data)
            notifiaction.create_notification(db_session)
            get_unscheduled  = db_session.query(UnscheduledMonitoring).filter(UnscheduledMonitoring.monitoring_case_id == get_loan_case.monitoring_case_id).order_by(UnscheduledMonitoring.id.desc()).first()
            new_loan_case_history = UnscheduledDeadlineExtensionMonitoringHistory(unscheduled_monitoring_id = get_unscheduled.id,
                                                    to_user_id = get_loan_case.second_responsible_id, 
                                                    from_user_id= get_loan_case.main_responsible_id,
                                                    comment = request.comment,
                                                    created_at = datetime.now(),
                                                    message = loan_case_history['deadline_extension_decline']
                                                        )
            db_session.add(new_loan_case_history)
            info_logger.info("user %s declined UNSCHEDULED deadline extension", get_loan_case.main_responsible_id)
        
    commit_object(db_session)
    
    return 'OK'







def get_case_deadline_extension(loan_case_id, case_type, db_session):
    if case_type == 1:
    
        get_target = db_session.query(TargetMonitoring).filter(TargetMonitoring.id == MonitoringCase.target_monitoring_id)\
            .filter(MonitoringCase.id == LoanCase.monitoring_case_id).filter(LoanCase.id == loan_case_id).first()
        if get_target is not None:
            target_extension_history = db_session.query(TargetDeadlineExtensionMonitoringHistory)\
                .filter(TargetDeadlineExtensionMonitoringHistory.target_monitoring_id == get_target.id).first()
        return return_object(target_extension_history, db_session)
    elif case_type == 2:
        get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == loan_case_id).first()
        get_scheduled  = db_session.query(ScheduledMonitoring).filter(ScheduledMonitoring.monitoring_case_id == get_loan_case.monitoring_case_id).order_by(ScheduledMonitoring.id.desc()).first()
        
        scheduled_extension_history = db_session.query(ScheduledDeadlineExtensionMonitoringHistory).filter(ScheduledDeadlineExtensionMonitoringHistory.scheduled_monitoring_id == get_scheduled.id)\
            .order_by(ScheduledDeadlineExtensionMonitoringHistory.id.desc()).first()
        
        return return_object(scheduled_extension_history, db_session)
        
    
    get_loan_case = db_session.query(LoanCase).filter(LoanCase.id == loan_case_id).first()
    get_unscheduled  = db_session.query(UnscheduledMonitoring).filter(UnscheduledMonitoring.monitoring_case_id == get_loan_case.monitoring_case_id).order_by(UnscheduledMonitoring.id.desc()).first()
    
    unscheduled_extension_history = db_session.query(UnscheduledDeadlineExtensionMonitoringHistory).filter(UnscheduledDeadlineExtensionMonitoringHistory.unscheduled_monitoring_id == get_unscheduled.id)\
        .order_by(UnscheduledDeadlineExtensionMonitoringHistory.id.desc()).first()
    
    return return_object(unscheduled_extension_history, db_session)
    



def get_case_deadline_extension_history(loan_case_id ,case_type, db_session):
    if case_type == 1:
        target_extension_history = []
        get_target = db_session.query(TargetMonitoring).filter(MonitoringCase.target_monitoring_id == TargetMonitoring.id)\
            .filter(LoanCase.monitoring_case_id == MonitoringCase.id).filter(LoanCase.id == loan_case_id).first()
        target_extension_history = db_session.query(TargetDeadlineExtensionMonitoringHistory).filter(TargetDeadlineExtensionMonitoringHistory.target_monitoring_id == get_target.id).all()
        return return_object_list(target_extension_history, db_session)
    elif case_type == 2:
        scheduled_extension_history = []
        get_scheduled = db_session.query(ScheduledMonitoring).filter(MonitoringCase.id == ScheduledMonitoring.monitoring_case_id)\
            .filter(LoanCase.monitoring_case_id == MonitoringCase.id).filter(LoanCase.id == loan_case_id).order_by(ScheduledMonitoring.id.desc()).first()
        if get_scheduled is not None:
            scheduled_extension_history = db_session.query(ScheduledDeadlineExtensionMonitoringHistory).filter(ScheduledDeadlineExtensionMonitoringHistory.scheduled_monitoring_id == get_scheduled.id).all()
        
        return return_object_list(scheduled_extension_history, db_session)
    unscheduled_extension_history = []
    get_unscheduled = db_session.query(UnscheduledMonitoring).filter(MonitoringCase.id == UnscheduledMonitoring.monitoring_case_id)\
            .filter(LoanCase.monitoring_case_id == MonitoringCase.id).filter(LoanCase.id == loan_case_id).order_by(UnscheduledMonitoring.id.desc()).first()   
    unscheduled_extension_history = db_session.query(UnscheduledDeadlineExtensionMonitoringHistory).filter(UnscheduledDeadlineExtensionMonitoringHistory.unscheduled_monitoring_id == get_unscheduled.id).all()
    
    return return_object_list(unscheduled_extension_history, db_session)

 
   
   
   
   
def return_object_list(case_extension_history, db_session):
    case_history = []
    if case_extension_history is not None:
        for extension_history in case_extension_history:
            from_user =  users.get_user_by_id(extension_history.from_user_id, db_session)
            to_user = users.get_user_by_id(extension_history.to_user_id, db_session)
            case_history.append({"id":extension_history.id,
                            "from_user": from_user,
                            "to_user": to_user,
                            "created_at": extension_history.created_at,
                            "updated_at": extension_history.updated_at,
                            "comment": extension_history.comment,
                            "message": extension_history.message,
                            'files': extension_history.files and files_crud.get_case_files(extension_history)})
    
    return case_history


def return_object(case_extension_history, db_session):
    case_history = []
    
    from_user =  users.get_user_by_id(case_extension_history.from_user_id, db_session)
    to_user = users.get_user_by_id(case_extension_history.to_user_id, db_session)
    case_history.append({"id":case_extension_history.id,
                    "from_user": from_user,
                    "to_user": to_user,
                    "created_at": case_extension_history.created_at,
                    "updated_at": case_extension_history.updated_at,
                    "comment": case_extension_history.comment,
                    "message": case_extension_history.message,
                    'files': case_extension_history.files and files_crud.get_case_files(case_extension_history)})
    return case_history






def get_case_hitory_type(db_session):
    case_history = []
    get_caset_type  = db_session.query(CaseHistoryType).all()
    for type in get_caset_type:
        case_history.append({"id":type.id,
                        "name": type.name,
                        "code": type.code})
    
    return case_history