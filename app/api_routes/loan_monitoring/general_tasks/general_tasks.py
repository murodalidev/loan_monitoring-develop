from fastapi import APIRouter
from app.services.loan_monitoring.general_tasks import general_tasks_crud
from app.db.connect_db import SessionManager
from app.schemas.general_tasks_schemas import General_tasks_request_schema, General_tasks_request_schema_update
from app.middleware.auth_file import AuthHandler

auth_handler = AuthHandler()

router = APIRouter(
    prefix = "/general-tasks", tags=["General Tasks"]
)

@router.get('/v1/get/{category_id}')
def tasks_by_category_page(category_id: int):
    with SessionManager() as db_session:
        tasks = general_tasks_crud.get_general_tasks_by_category_id(category_id, db_session)
    return {"Tasks":tasks}


@router.post('/v1/create')
def general_tasks_add(request: General_tasks_request_schema):
    with SessionManager() as db_session:
        status = general_tasks_crud.create_general_tasks(request, db_session)
    return status



@router.put('/v1/update/{id}')
def general_tasks_update(id:int, request: General_tasks_request_schema_update):
    with SessionManager() as db_session:
        status = general_tasks_crud.update_general_tasks(id, request, db_session)
    return status


@router.delete('/v1/delete/{id}')
def general_tasks_delete(id:int):
    with SessionManager() as db_session:
        status = general_tasks_crud.delete_general_tasks(id, db_session)
    return status