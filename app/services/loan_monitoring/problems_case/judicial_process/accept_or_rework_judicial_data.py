import datetime

from app.models.monitoring_case.reslut_reason_model import ResultReason
from app.models.problems_case.problems_case_model import ProblemsCase
from app.models.problems_case.problems_assets.problems_assets_notification_model import ProblemsStateNotification
from app.models.problems_case.judicial_process.judicial_data_history_model import JudicialDataHistory
from app.models.problems_case.problems_monitoring_expiration_model import ProblemsMonitoringExpiration
from app.models.problems_case.problems_monitoring_model import ProblemsMonitoring
from app.models.problems_case.judicial_process.judicial_data_history_model import JudicialDataHistory

from .....models.problems_case.judicial_process.judicial_process_data_model import JudicialData
from .....models.problems_case.judicial_process.judicial_authority import JudicialAuthority
from .....models.loan_case.loan_case_model import LoanCase
from .....models.loan_case.loan_case_history_model import LoanCaseHistory
from .....models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_model import UnscheduledMonitoring, unscheduled_monitoring_files
from .....models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_history import UnscheduledMonitoringHistory
from .....models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_expiration_model import UnscheduledMonitoringExpiration
from .....models.statuses.monitoring_frequency_period_model import MonitoringFrequencyPeriod
from .....common.is_empty import is_empty, is_exists
from .....common.commit import commit_object, flush_object
from .....common import save_file
from dateutil.relativedelta import relativedelta
from .....schemas.juridical_case_schemas import SendToProblemAfterTarget
from ...juridical_case import juridical_case_crud
from ....monitoring_files import files_crud
from ...task_manager.task_manager_crud import TaskManager_class
from .....common.dictionaries.monitoring_case_dictionary import  problems_assets_status
from .....common.dictionaries.notification_dictionary import notification_type, notification_body
from .....common.dictionaries.case_history_dictionaries import loan_case_history, juridical_case_history
from .....common.dictionaries.task_status_dictionaries import task_status
from .....schemas.task_manager_schemas import CreateTaskManagerSetTargetMonitoring,UpdateTaskManagerSendToCheck, UpdateTaskManagerAccept, GetaskManager,UpdateTaskManagerClose
from ...notification.notification_crud import Notificaton_class
from .....schemas.notification_schemas import CreateNotification
from .....config.logs_config import info_logger
import os
from ...problems_case import non_targeted_case
from .....common.dictionaries.general_tasks_dictionary import JGT, MGT, MAIN_DUE_DATE, CASE_HISTORY, DEADLINE_EXT
from ...monitoring_case.script_date_holidays import get_business_days




def accept_or_rework_judicial_data(request, db_session):
    info_logger.info("user %s required 'accept_or_rework_judicial_data' method", request.from_user)
    judicial_data = db_session.query(JudicialData).filter(JudicialData.id == request.judicial_data_id).first()
    get_problems_case = db_session.query(ProblemsCase).filter(ProblemsCase.id == request.problems_case_id).first()
    get_problems_state_notification = db_session.query(ProblemsStateNotification).filter(ProblemsStateNotification.loan_portfolio_id == get_problems_case.loan_portfolio_id).first()
    if request.result_type:
        
        status = problems_assets_status['проверено']
        message = juridical_case_history['apply']
        body = notification_body['accept_juridical_data']
        
        judicial_data.problem_case.updated_at = datetime.datetime.now()
        get_problems_state_notification.judicial_status_id = problems_assets_status['проверено']
        
        new_judicial_data_history = JudicialDataHistory(problems_case_id = request.problems_case_id, 
                                            type_id = CASE_HISTORY.JUDICIAL.value,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = message
                                                )
        db_session.add(new_judicial_data_history)
        
        
        
        
    else:
        status = problems_assets_status['переделать']
        message = juridical_case_history['rework']
        body = notification_body['accept_juridical_data']
        
        file_path = files_crud.set_wrong_files(request.wrong_files, judicial_data, db_session)
        flush_object(db_session)
        info_logger.info("user %s sent problems_monitoring to rework", request.from_user)
        info_logger.info("user %s sent to rework files: %s", request.from_user, file_path)
        new_problems_monitoring_history = JudicialDataHistory(problems_case_id = request.problems_case_id,
                                            type_id = CASE_HISTORY.JUDICIAL.value,
                                            from_user_id = request.from_user, 
                                            to_user_id= request.to_user,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = message
                                                )
        db_session.add(new_problems_monitoring_history)
        
        
        get_problems_state_notification.judicial_status_id = problems_assets_status['переделать']
        
    judicial_data.judicial_status_id = status
    
    
    get_problems_case.updated_at = datetime.datetime.now()
    get_problems_case.checked_status=False
    
    data = CreateNotification()
    data.from_user_id = request.from_user 
    data.to_user_id =request.to_user
    data.notification_type = notification_type['problems']
    data.body = body
    data.url = f'{get_problems_case.loan_portfolio_id}' + ':' + f'{get_problems_case.id}'+ ':' +f'{MGT.JUDICIAL.value}'
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    
    
    
    commit_object(db_session)
    
    return "OK"