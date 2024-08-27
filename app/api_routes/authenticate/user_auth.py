from fastapi import APIRouter, Request
from app.services.users import user_login
from app.db.connect_db import SessionManager
from app.schemas.user_schemas import UserLogin

router = APIRouter(
    prefix = "/user", tags=["Login"]
)

#Авторизация пользователя
@router.post('/login',status_code=200)
def get_token(user:UserLogin, request: Request):
    with SessionManager() as db_session:
        status = user_login.login_user(user, db_session)
        
    return status