from fastapi import APIRouter, Form, Depends
from app.db.connect_db import SessionManager
from app.middleware.auth_file import AuthHandler
from ...services.rbac import roles
from ...services.rbac import permission_crud
from ...schemas.rbac_schemas import Role, User_role
router = APIRouter(
    prefix = "/role", tags=["RBAC ROLE"]
)


@router.get('/v1/read/all')
def user_role_page():
    with SessionManager() as db_session:
        user_type = roles.get_all_user_roles(db_session)
    return user_type


@router.get('/v1/get/permissions/all')
def user_permissions():
    with SessionManager() as db_session:
        
        permissions = roles.get_all_permissions(db_session)
    return permissions


@router.get('/v1/get/permissions/for/role/{id}')
def role_permissions(id:int):
    with SessionManager() as db_session:
        
        permissions = permission_crud.get_role_permissions(id, db_session)
    return permissions



@router.post('/v1/create')
def user_typr_add(request: Role):
    with SessionManager() as db_session:
        
        status = roles.create_user_role(request, db_session)
    return status

@router.put('/v1/update/{roleid}')
def user_type_update(roleid:int, request: Role):
    with SessionManager() as db_session:
        
        status = roles.update_user_role(roleid, request, db_session)
    return status


@router.delete('/v1/delete/{id}')
def user_type_delete(id:int):
    with SessionManager() as db_session:
        status = roles.delete_user_role(id, db_session)
    return status


@router.get('/v1/get-user-roles/{userid}')
def delete_appended_role(userid:int):
    with SessionManager() as db_session:
        status = roles.get_user_roles(userid, db_session)
    return status

@router.get('/v1/append-user-role/users')
def role_permissions():
    with SessionManager() as db_session:
        status = roles.append_role_user_to_all_users(db_session)
    return status


@router.post('/v1/user/append-to-user/{userid}')
def user_append_role(userid:int, request: User_role):
    with SessionManager() as db_session:
        status = roles.append_user_role(userid, request, db_session)
    return status


@router.delete('/v1/delete-appended-for-user/{userid}')
def delete_appended_role(userid:int):
    with SessionManager() as db_session:
        status = roles.delete_appended_user_role(userid, db_session)
    return status


