from fastapi import HTTPException
from app.middleware.auth_file import AuthHandler
from app.models.users.users import Users
from .users_crud import Users as user_class
import logging
logger = logging.getLogger(__name__)

auth_handler = AuthHandler()


def login_user(user,  db_session):
    logger.info("User requires login.")
    get_user = db_session.query(Users).filter(Users.username == user.username).first()
    # if user.password == 'asdfqwer':
    #     access_token = auth_handler.encode_token(get_user.username)
    #     user_data = user_class.get_all_data_for_user(get_user, db_session)
    #     return { 'token': access_token,
    #             'password_status':get_user.password_status,
    #             'data':user_data}
    
    if (get_user is None) or (not auth_handler.verify_password(user.password, get_user.password)):
        logger.info("Incorrect password or login!")
        raise HTTPException(status_code=400, detail='Пароль ёки Логин нотўғри ёзилган!')
    access_token = auth_handler.encode_token(get_user.username)
    real_ip=None
    user_class.save_user_token_and_ip(get_user, access_token, real_ip, db_session)
    user_data = user_class.get_all_data_for_user(get_user, db_session)
    logger.info("User successfully logged in.")
    return { 'token': access_token,
            'password_status':get_user.password_status,
            'data':user_data}
