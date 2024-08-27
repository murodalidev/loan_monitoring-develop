from fastapi import APIRouter
import logging
from app.middleware.auth_file import AuthHandler
from app.services.users.users_crud import Users, get_data_for_crud
from app.db.connect_db import SessionManager
from app.schemas.user_schemas import UserCrud, UserLogin
from app.services.users.user_tg_bot import check_exist_user, get_user_by_param, create_user, get_active_notification, get_deadlines
auth_handler = AuthHandler()

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix = "/user-tg-bot", tags=["User Tg Bot"]
)


@router.put('/v1/registration')
def registrate_user(tg_user_id: int = None, user_id: int = None):
    with SessionManager() as db_session:
        status = create_user(db_session, tg_user_id, user_id)
    return status

@router.get('/v1/check_tg_user')
def check_user(tg_user_id: int = None, user_id: int = None, token: str = None):
    with SessionManager() as db_session:
        status = check_exist_user(db_session, tg_user_id, user_id, token)
    return status

@router.get('/v1/get_user')
def get_user(user_id: int = None, username: str = None):
    with SessionManager() as db_session:
        status = get_user_by_param(db_session, user_id, username)
    return status

@router.get('/v1/get_notifications')
def get_notification(user_id: int, page: int):
    with SessionManager() as db_session:
        status = get_active_notification(db_session, user_id, page)
    return status

@router.get('/v1/get_deadlines')
def deadlines(user_id: int, days: int = 3, page: int = 0):
    with SessionManager() as db_session:
        status = get_deadlines(db_session, user_id, days, page)
    return status