from fastapi import APIRouter
import logging
from app.middleware.auth_file import AuthHandler
from app.services.users import attached_regions
from app.db.connect_db import SessionManager
from fastapi import APIRouter, Depends
from app.schemas.user_schemas import  BranchesToUser, RegionsToUser
auth_handler = AuthHandler()

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix = "/regions-user", tags=["Attach Regions"]
)

@router.post('/v1/attach/region')
def attach_local_codes_to_user(request:RegionsToUser):
    with SessionManager() as db_session:
        status = attached_regions.attach_regions_to_user(request, db_session)
    return status



@router.get('/v1/attached-regions/get')
def get_attached_branches(user_id:int=None, region_id:int=None, department_id:int=None, attach_type_id:int=None, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        data = attached_regions.get_user_attached_regions(user, user_id, region_id, department_id, attach_type_id, db_session)
    return data


@router.get('/v1/attached-types/get')
def data_for_crud():
    with SessionManager() as db_session:
        data = attached_regions.get_attached_types(db_session)
    return data


@router.get('/v1/attached-users/get')
def data_for_crud(local_code_id:int=None, attached_type:int=None, main_responsible:int=None, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        data = attached_regions.get_attached_regions_users(user, user.department, main_responsible, attached_type, local_code_id, db_session)
    return data

@router.get('/v1/attached-users/for-main-superviser/get')
def attached(local_code_id:int=None, attached_type:int=None, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        data = attached_regions.get_attached_users_for_main_superviser(user, user.department, attached_type, local_code_id, db_session)
    return data

