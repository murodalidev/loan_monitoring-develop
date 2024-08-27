from datetime import datetime, timedelta
from ....models.files.monitoring_files_model import MonitoringFiles
from ....models.monitoring_case.monitoring_case_model import MonitoringCase
from ....models.loan_case.loan_case_model import LoanCase
from ....models.monitoring_case.scheduled_monitoring_history_model import ScheduledMonitoringHistory
from ....models.monitoring_case.target_monitoring_model import TargetMonitoring
from ....models.statuses.target_monitoring_result_model import TargetMonitoringResult
from ....common.is_empty import is_empty, is_empty_list, is_exists
from ....common.commit import commit_object, flush_object
from ..task_manager.task_manager_crud import TaskManager_class
from ....schemas.task_manager_schemas import UpdateTaskManagerSetResponsible
from ....common.dictionaries.task_status_dictionaries import task_status
from ....common.dictionaries.case_history_dictionaries import loan_case_history
from ....common.dictionaries.notification_dictionary import notification_type, notification_body, notification_url
from ....schemas.task_manager_schemas import CreateTaskManagerSetTargetMonitoring, GetaskManager, UpdateTaskManagerSendToCheck, UpdateTaskManagerAccept, UpdateTaskManagerClose
from ..notification.notification_crud import Notificaton_class
from ....schemas.notification_schemas import CreateNotification
from ....schemas.juridical_case_schemas import SendToJuridicAfterTarget
from  app.services.users.users_crud import Users as users
from . import monitoring_case_crud
from ....services.monitoring_files import files_crud
from ..juridical_case import juridical_case_crud
from sqlalchemy import or_
from ....common.dictionaries.departments_dictionary import DEP
from ....common.dictionaries.general_tasks_dictionary import JGT, MGT, PGT, GTCAT








def get_scheduled_history(monitoring_id, db_session):
    case_history = []
    
    scheduled_history = db_session.query(ScheduledMonitoringHistory).filter(ScheduledMonitoringHistory.monitoring_case_id == monitoring_id)\
        .order_by(ScheduledMonitoringHistory.created_at.asc()).all()
    
    
    for history in scheduled_history:
        from_user =  users.get_user_by_id(history.from_user_id, db_session)
        to_user = users.get_user_by_id(history.to_user_id, db_session)
        case_history.append({"id":history.id,
                             "from_user": from_user,
                             "to_user": to_user,
                             "created_at": history.created_at,
                             "updated_at": history.updated_at,
                             "comment": history.comment,
                             "message": history.message,
                             "additional_data": history.additional_data})
        
    return case_history