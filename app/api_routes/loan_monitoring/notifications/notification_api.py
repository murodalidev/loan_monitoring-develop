from fastapi import APIRouter, Depends
from app.services.loan_monitoring.notification.notification_crud import Notificaton_class
from app.db.connect_db import SessionManager
from ....schemas.notification_schemas import ReadNotification
from app.middleware.auth_file import AuthHandler
from typing import List
auth_handler = AuthHandler()

router = APIRouter(
    prefix = "/notifications", tags=["Notifications"]
)


@router.get('/v1/get/')
def active_notifications_page(page:int, size:int,user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        notifications = Notificaton_class.get_all(page, size, user, db_session)
    return {"active_notifications": notifications}



@router.put('/v1/read/{notification_id}')
def read_notification(notification_id:int, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        notif_data = ReadNotification()
        notif_data.user_id = user.id
        notif_data.notification_id = notification_id
        update_notification = Notificaton_class(notif_data)
        status = update_notification.read_notification(db_session)

    return status



@router.get('/v1/read/all')
def read_all_notification(user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        notif_data = ReadNotification()
        notif_data.user_id = user.id
        update_notification = Notificaton_class(notif_data)
        status = update_notification.read_all(db_session)

    return status



@router.post('/v1/read/all/for-user')
def read_all_notification(notification_ids:List[int],user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        notif_data = ReadNotification()
        notif_data.user_id = user.id
        notif_data.notifications = notification_ids
        update_notification = Notificaton_class(notif_data)
        status = update_notification.read_all_for_user(db_session)

    return status