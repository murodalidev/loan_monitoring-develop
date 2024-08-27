from fastapi import APIRouter
from app.services.loan_monitoring.notification.notification_crud import Notificaton_class
from app.db.connect_db import SessionManager
from app.middleware.auth_file import AuthHandler
from app.schemas.notification_schemas import Notification_request

auth_handler = AuthHandler()

router = APIRouter(
    prefix = "/notifications", tags=["Notifications"]
)


@router.get('/v1/get/{user_id}')
def active_notifications_page(user_id: int):
    with SessionManager() as db_session:
        notifications = Notificaton_class.get_all(user_id, db_session)
    return {"active_notifications": notifications}

@router.put('/v1/read')
def make_read(user_data: Notification_request):
    with SessionManager() as db_session:
        update_notification = Notificaton_class(user_data)
        status = Notificaton_class.has_been_read(user_data, db_session)

    return status