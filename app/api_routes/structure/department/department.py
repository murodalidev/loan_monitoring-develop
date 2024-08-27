from fastapi import APIRouter, Depends
from app.services.structure.department import department_crud
from app.services.structure.region import region_crud
from app.db.connect_db import SessionManager
from app.schemas.department_schemas import Departments_request_schema
from app.middleware.auth_file import AuthHandler


auth_handler = AuthHandler()
router = APIRouter(
    prefix = "/department", tags=["Departments"]
)


@router.get('/v1/read/all')
def department_page():
    with SessionManager() as db_session:
        departments = department_crud.get_all_departments(db_session)
    return {"departments":departments}

@router.get('/v1/data-for-create/get')
def get_branches():
    with SessionManager() as db_session:
        branches = region_crud.get_all_regions(db_session)
    return {"branches":branches}



@router.post('/v1/create')
def department_add(request: Departments_request_schema):
    with SessionManager() as db_session:
        status = department_crud.create_department(request, db_session)
    return status



@router.put('/v1/update/{id}')
def department_update(id:int, request: Departments_request_schema):
    with SessionManager() as db_session:
        status = department_crud.update_department(id, request, db_session)
    return status


@router.delete('/v1/delete/{id}')
def department_delete(id:int):
    with SessionManager() as db_session:
        status = department_crud.delete_department(id, db_session)
    return status