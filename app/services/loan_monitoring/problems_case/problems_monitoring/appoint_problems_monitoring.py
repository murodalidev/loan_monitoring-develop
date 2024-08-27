import datetime

from app.models.monitoring_case.reslut_reason_model import ResultReason
from app.models.problems_case.problems_case_model import ProblemsCase
from app.models.problems_case.problems_monitoring_history_model import ProblemsMonitoringHistory
from app.models.problems_case.problems_monitoring_model import ProblemsMonitoring
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
from .....common import save_file
from dateutil.relativedelta import relativedelta
from .....schemas.juridical_case_schemas import SendToProblemAfterTarget
from ...juridical_case import juridical_case_crud
from ....monitoring_files import files_crud
from ...task_manager.task_manager_crud import TaskManager_class
from .....common.dictionaries.monitoring_case_dictionary import  monitoring_status
from .....common.dictionaries.notification_dictionary import notification_type, notification_body
from .....common.dictionaries.case_history_dictionaries import loan_case_history, problem_case_history
from .....common.dictionaries.task_status_dictionaries import task_status
from .....schemas.task_manager_schemas import CreateTaskManagerSetTargetMonitoring,UpdateTaskManagerSendToCheck, UpdateTaskManagerAccept, GetaskManager,UpdateTaskManagerClose
from ...notification.notification_crud import Notificaton_class
from .....schemas.notification_schemas import CreateNotification
from .....config.logs_config import info_logger
import os
from ...problems_case import non_targeted_case
from .....common.dictionaries.general_tasks_dictionary import JGT, MGT, MAIN_DUE_DATE, CASE_HISTORY, DEADLINE_EXT









def appoint_problems_monitoring(request, db_session):
    info_logger.info("user %s required 'appoint_problems_monitoring' method", request.main_responsible_id)
    
    new_problems_monitoring = ProblemsMonitoring(problems_case_id = request.problems_case_id,
                                             problems_monitoring_status_id = monitoring_status['назначен'],
                                             created_at = datetime.datetime.now().date(),
                                             deadline = request.deadline)
    
    db_session.add(new_problems_monitoring)
    flush_object(db_session)
    
    get_problems_case = db_session.query(ProblemsCase).filter(ProblemsCase.id == request.problems_case_id).first()
    
    data = CreateNotification()
    data.from_user_id = request.main_responsible_id
    data.to_user_id = request.second_responsible_id
    data.notification_type = notification_type['problems']
    data.body = notification_body['problems_monitoring_appoint']
    data.url = f'{get_problems_case.loan_portfolio_id}' + ':' + f'{get_problems_case.id}'+ ':' +f'{MGT.PROBLEMS.value}'
    
    notifiaction = Notificaton_class(data)
    notifiaction.create_notification(db_session)
    get_problems_case.updated_at = datetime.datetime.now()
    get_problems_case.checked_status=False
    new_problems_history = ProblemsMonitoringHistory(problems_monitoring_id = new_problems_monitoring.id, 
                                            type_id = CASE_HISTORY.PROBLEMS.value,
                                            from_user_id = request.main_responsible_id, 
                                            to_user_id= request.second_responsible_id,
                                            comment = request.comment,
                                            created_at = datetime.datetime.now(),
                                            message = problem_case_history['problems_monitoring_appoint']
                                                )
    db_session.add(new_problems_history)
    commit_object(db_session)
    
    return {"OK"}