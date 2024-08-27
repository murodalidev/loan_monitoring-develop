from .....models.monitoring_case.unscheduled_monitoring.unscheduled_monitoring_history import UnscheduledMonitoringHistory
from  app.services.users.users_crud import Users as users








def get_unscheduled_history(monitoring_id, db_session):
    unscheduled_history = []
    
    get_unscheduled_history = db_session.query(UnscheduledMonitoringHistory).filter(UnscheduledMonitoringHistory.monitoring_case_id == monitoring_id)\
        .order_by(UnscheduledMonitoringHistory.created_at.asc()).all()
    
    
    for history in get_unscheduled_history:
        from_user =  users.get_user_by_id(history.from_user_id, db_session)
        to_user = users.get_user_by_id(history.to_user_id, db_session)
        unscheduled_history.append({"id":history.id,
                             "from_user": from_user,
                             "to_user": to_user,
                             "created_at": history.created_at,
                             "updated_at": history.updated_at,
                             "comment": history.comment,
                             "message": history.message,
                             "additional_data": history.additional_data})
        
    return unscheduled_history