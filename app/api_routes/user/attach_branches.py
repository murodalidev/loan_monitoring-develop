from fastapi import APIRouter
import logging
from app.middleware.auth_file import AuthHandler
from app.services.users import attached_branches_crud, attached_regions
from app.db.connect_db import SessionManager
from fastapi import APIRouter, Depends
from app.schemas.user_schemas import  BranchesToUser, LocalsToUser
auth_handler = AuthHandler()

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix = "/branches-user", tags=["Attach Branches"]
)

@router.post('/v1/attach/local-code')
def attach_local_codes_to_user(request:LocalsToUser):
    with SessionManager() as db_session:
        status = attached_branches_crud.attach_local_codes_to_user(request, db_session)
    return status



@router.get('/v1/attached-locals/get')
def get_attached_branches(user_id:int=None, region_id:int=None, department_id:int=None, attach_type_id:int=None, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        data = attached_branches_crud.get_user_attached_locals(user, user_id, region_id, department_id, attach_type_id, db_session)
    return data


@router.get('/v1/attached-types/get')
def data_for_crud():
    with SessionManager() as db_session:
        data = attached_branches_crud.get_attached_types(db_session)
    return data


@router.get('/v1/attached-users/get')
def data_for_crud(local_code_id:int=None, attached_type:int=None, main_responsible:int=None, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        data = attached_regions.get_attached_regions_users(user, user.department, main_responsible, attached_type, local_code_id, db_session)
        #data = attached_branches_crud.get_attached_locals_users(user, user.department, main_responsible, attached_type, local_code_id, db_session)
    return data

@router.get('/v1/attached-users/for-main-superviser/get')
def attached(local_code_id:int=None, attached_type:int=None, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        data = attached_regions.get_attached_users_for_main_superviser(user, user.department, attached_type, local_code_id, db_session)
        #data = attached_branches_crud.get_attached_users_for_main_superviser(user, user.department, attached_type, local_code_id, db_session)
    return data


# @router.get('/v1/get/by-param')
# def data_for_crud(bank_mfo:str=None, department:int=None, user_name:str=None):
#     with SessionManager() as db_session:
#         data = Users.get_users_by_param(bank_mfo, department, user_name, db_session)
#     return {"users":data}



# @router.put('/v1/update/{id}')
# def update_user(id:int, user_data:UserCrud):
#     with SessionManager() as db_session:
#         update_user = Users(user_data)
#         status = update_user.update(id, db_session)
#     return status

# @router.put('/v1/update/data/{id}')
# def update_user_data(id:int, user_data:UserLogin):
#     with SessionManager() as db_session:
#         update_user = Users(user_data)
#         status = update_user.update_login_password(id, db_session)
#     return status



# @router.delete('/v1/delete/{id}')
# def delete_user(id:int):
#     with SessionManager() as db_session:
#         user = Users()
#         status = user.delete(id, db_session)
#     return status