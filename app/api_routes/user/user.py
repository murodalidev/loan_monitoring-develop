from fastapi import APIRouter
import logging
from app.middleware.auth_file import AuthHandler
from app.services.users.users_crud import Users, get_data_for_crud
from app.db.connect_db import SessionManager
from fastapi import APIRouter, Depends
from app.schemas.user_schemas import UserCrud, UserLogin
auth_handler = AuthHandler()

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix = "/user", tags=["User CRUD"]
)


@router.post('/v1/create')
def create_user(user_data:UserCrud):
    with SessionManager() as db_session:
        new_user = Users(user_data, 'create')
        status = new_user.create(db_session)
    return status

@router.get('/v1/data-for-crud/get')
def data_for_crud():
    with SessionManager() as db_session:
        data = get_data_for_crud(db_session)
    return data

@router.get('/v1/get/all')
def data_for_crud():
    with SessionManager() as db_session:
        data = Users.get_all(db_session)
    return {"users":data}

@router.get('/v1/get/by-param')
def user_get_by_param(size:int=None, page:int=None, full_name:str=None, user_name:str=None, region:str=None, local_code:str=None, department:int=None, position:str=None):
    with SessionManager() as db_session:
        data = Users.get_users_by_param(size, page, full_name, user_name, region, local_code, department, position, db_session)
    return {"users":data}


@router.get('/v1/get/by-local')
def user_get_by_param(local_code:int=None, attach_type_id:int=None,  department:int=None, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        data = Users.get_user_by_local(user.id, local_code, department, db_session, attach_type_id)
    return {"users":data}


@router.put('/v1/update/{id}')
def update_user(id:int, user_data:UserCrud):
    with SessionManager() as db_session:
        update_user = Users(user_data)
        status = update_user.update(id, db_session)
    return status

@router.put('/v1/update/data/{id}')
def update_user_data(id:int, user_data:UserLogin):
    with SessionManager() as db_session:
        update_user = Users(user_data)
        status = update_user.update_login_password(id, db_session)
    return status

@router.post('/v1/update/password')
def update_user_password(old_password:str, user_data:UserCrud, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        update_user = Users(user_data, 'update')
        status = update_user.update_password(user, old_password, db_session)
    return status

@router.post('/v1/update/username')
def update_user_username(user_data:UserCrud, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        update_user = Users(user_data)
        status = update_user.update_username(user, db_session)
    return status

@router.post('/v1/refresh/password/{id}')
def update_user_password(id:int, user_data:UserCrud, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        update_user = Users(user_data, 'reset')
        status = update_user.refresh_password(user, id, db_session)
    return status

@router.delete('/v1/delete/{id}')
def delete_user(id:int):
    with SessionManager() as db_session:
        user = Users()
        status = user.delete(id, db_session)
    return status