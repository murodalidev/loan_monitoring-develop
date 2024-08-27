from fastapi import APIRouter
from app.services.loan_monitoring.general_tasks import general_tasks_category_crud
from app.db.connect_db import SessionManager
from app.schemas.general_tasks_category_schemas import General_tasks_category_request_schema
from app.middleware.auth_file import AuthHandler

auth_handler = AuthHandler()

router = APIRouter(
    prefix = "/general-tasks-category", tags=["General Tasks Category"]
)

@router.get('/v1/get/all')
def category_page():
    with SessionManager() as db_session:
        category = general_tasks_category_crud.get_all(db_session)
    return {"Category":category}


@router.post('/v1/create')
def category_add(request: General_tasks_category_request_schema):
    with SessionManager() as db_session:
        status = general_tasks_category_crud.create_general_tasks_category(request, db_session)
    return status



@router.put('/v1/update/{id}')
def category_update(id:int, request: General_tasks_category_request_schema):
    with SessionManager() as db_session:
        status = general_tasks_category_crud.update_general_tasks_category(id, request, db_session)
    return status


@router.delete('/v1/delete/{id}')
def category_delete(id:int):
    with SessionManager() as db_session:
        status = general_tasks_category_crud.delete_general_tasks_category(id, db_session)
    return status