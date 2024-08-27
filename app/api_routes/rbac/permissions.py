from fastapi import APIRouter,Depends
from app.db.connect_db import SessionManager
from app.services.rbac import permission_crud
from app.schemas.rbac_schemas import Name_for_path, PermissionToUser
router = APIRouter(
    prefix = "/permission", tags=["RBAC"]
)

@router.get('/v1/read/all')
def roles_permissions_page():
    with SessionManager() as db_session:
        data = permission_crud.get_all_path_tags(db_session)
    return data



@router.post('/v1/name-for-path/create')
def name_for_path(request: Name_for_path):
    with SessionManager() as db_session:
        status = permission_crud.set_name_for_paths(request, db_session)
    return status



@router.post('/v1/permission-to-role/append-or-remove')
def permission_to_user(request: PermissionToUser):
    with SessionManager() as db_session:
        status = permission_crud.append_or_remove_permission(request, db_session)
    return status

@router.post('/v1/all/append-to-superuser')
def permission_to_user():
    with SessionManager() as db_session:
        status = permission_crud.append_all_permissions_to_role(db_session)
    return status


@router.delete('/v1/delete-permission/from-role/{id}')
def delete_user_permissions(id:int):
    with SessionManager() as db_session:
        status = permission_crud.delete_role_permissions(id, db_session)
    return status