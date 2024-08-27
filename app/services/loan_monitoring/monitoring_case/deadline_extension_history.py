from datetime import datetime
from ....models.monitoring_case.extension_history_model import ScheduledDeadlineExtensionMonitoringHistory, TargetDeadlineExtensionMonitoringHistory
from  app.services.users.users_crud import Users as users
from sqlalchemy import or_
from ....common.dictionaries.departments_dictionary import DEP
from ....common.dictionaries.general_tasks_dictionary import JGT, MGT, PGT, GTCAT








def get_scheduled_deadline_extension_history(target_extension_history_id, db_session):
    case_history = []
    
    scheduled_extension_history = db_session.query(ScheduledDeadlineExtensionMonitoringHistory)\
        .filter(ScheduledDeadlineExtensionMonitoringHistory.scheduled_monitoring_id == target_extension_history_id)\
            .order_by(ScheduledDeadlineExtensionMonitoringHistory.created_at.asc()).all()
    
    
    for history in scheduled_extension_history:
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




def get_target_deadline_extension_history(target_extension_history_id, db_session):
    case_history = []
    
    target_extension_history = db_session.query(TargetDeadlineExtensionMonitoringHistory)\
        .filter(TargetDeadlineExtensionMonitoringHistory.target_monitoring_id == target_extension_history_id)\
            .order_by(TargetDeadlineExtensionMonitoringHistory.created_at.asc()).all()
    
    
    for history in target_extension_history:
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