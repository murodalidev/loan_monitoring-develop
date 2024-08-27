from fastapi import APIRouter, Depends
from app.services.structure.position import position_crud
from app.db.connect_db import SessionManager
from app.schemas.position_schema import Position_request_schema
from app.middleware.auth_file import AuthHandler


auth_handler = AuthHandler()
router = APIRouter(
    prefix = "/position", tags=["Positions"]
)


@router.get('/v1/read/all')
def position_page():
    with SessionManager() as db_session:
        positions = position_crud.get_all_positions(db_session)
    return {"positions":positions}


@router.post('/v1/create')
def position_add(request: Position_request_schema):
    with SessionManager() as db_session:
        status = position_crud.create_position(request, db_session)
    return status



@router.put('/v1/update/{id}')
def position_update(id:int, request: Position_request_schema):
    with SessionManager() as db_session:
        status = position_crud.update_position(id, request, db_session)
    return status


@router.delete('/v1/delete/{id}')
def position_delete(id:int):
    with SessionManager() as db_session:
        status = position_crud.delete_position(id, db_session)
    return status