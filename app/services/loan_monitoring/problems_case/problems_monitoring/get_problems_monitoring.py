import datetime

from app.models.monitoring_case.reslut_reason_model import ResultReason
from app.models.problems_case.problems_case_model import ProblemsCase
from app.models.problems_case.problems_monitoring_history_model import ProblemsMonitoringHistory
from app.models.problems_case.problems_monitoring_expiration_model import ProblemsMonitoringExpiration
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




def get_all_problems_monitoring(problems_case_id, db_session):
    problem = []
    get_problems_monitoring = db_session.query(ProblemsMonitoring).filter(ProblemsMonitoring.problems_case_id == problems_case_id).order_by(ProblemsMonitoring.id.asc()).all()
    is_exists(get_problems_monitoring, 400, 'Problems monitoring not found')
    
    for  problems in get_problems_monitoring:
        problem.append({'id': problems.id,
                          'problems_monitoring_status': problems.problems_monitoring_status_id and problems.status or None,
                          'created_at':problems.created_at,
                          'deadline':problems.deadline,
                          'updated_at':problems.updated_at,
                          'files': problems.files and files_crud.get_case_files(problems)})
        
    return problem
        

    
def get_problems_case_details(id, db_session):
    problem_case = {}
    get_problems_case = db_session.query(ProblemsCase).filter(ProblemsCase.id == id).first()
    
    if get_problems_case is not None:
        problem_case ={"id":get_problems_case.id,
                       "loan_portfolio":{"id":get_problems_case.portfolio.id,
                                        "local_code":{ "id":get_problems_case.portfolio.local_code.id,
                                                        "code":get_problems_case.portfolio.local_code.code,
                                                        "name":get_problems_case.portfolio.local_code.name}},
                            "main_responsible":{"id":get_problems_case.main_responsible_id and get_problems_case.main_responsible.id,
                                          "full_name":get_problems_case.main_responsible_id and get_problems_case.main_responsible.full_name,
                                          "local_code":{"id":get_problems_case.main_responsible_id and get_problems_case.main_responsible.local.id,
                                                        "code":get_problems_case.main_responsible_id and get_problems_case.main_responsible.local.code,
                                                        "name":get_problems_case.main_responsible_id and get_problems_case.main_responsible.local.name}},
                            "second_responsible":{"id":get_problems_case.second_responsible and get_problems_case.second_responsible.id,
                                          "full_name":get_problems_case.second_responsible and get_problems_case.second_responsible.full_name,
                                          "local_code":{"id":get_problems_case.main_responsible_id and get_problems_case.second_responsible.local.id,
                                                        "code":get_problems_case.main_responsible_id and get_problems_case.second_responsible.local.code,
                                                        "name":get_problems_case.main_responsible_id and get_problems_case.second_responsible.local.name}},
                            "deadline_extension_status":get_problems_case.deadline_extension_status_id and get_problems_case.deadline_extension_status_id or None,
                            
                            "created_at":get_problems_case.created_at and get_problems_case.created_at or None,
                            "updated_at":get_problems_case.updated_at and get_problems_case.updated_at or None}
        
        return {"loan_case":problem_case}