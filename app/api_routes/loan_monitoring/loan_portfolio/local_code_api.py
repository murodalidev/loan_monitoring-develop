from fastapi import APIRouter, Depends
from app.services.loan_monitoring.directories import local_code_crud
from app.services.structure.region import region_crud
from app.db.connect_db import SessionManager
from ....common import common_handler
from app.schemas.loan_product_schemas import LoanProduct, LocalCode
from app.middleware.auth_file import AuthHandler


auth_handler = AuthHandler()
router = APIRouter(
    prefix = "/local-code", tags=["Local Code"]
)



@router.get('/v1/load/all')
def load_local_code():
    with SessionManager() as db_session:
        common_handler.handle_error(local_code_crud.load_local_code_v2, db_session)
    return {'OK'}


@router.get('/v1/read/all')
def local_code_get_all(region_id:int=None):
    with SessionManager() as db_session:
        response = common_handler.handle_error(local_code_crud.get_all_local_codes,  db_session, region_id)
    return response

@router.get('/v1/get-by-param')
def local_code_get_by_param(size:int, page:int, region_id:int=None, local_code:int=None, name:str=None):
    with SessionManager() as db_session:
        response = common_handler.handle_error(local_code_crud.get_local_codes_by_param, size, page,region_id, local_code, name, db_session)
    return response

@router.get('/v1/get-for-filter')
def local_code_get_for_filter(region_id:int=None):
    with SessionManager() as db_session:
        response = common_handler.handle_error(local_code_crud.get_local_codes_for_filter, region_id, db_session)
    return response



# @router.get('/v1/get-by-mfo')
# def local_code_get_by_mfo(mfo_id:int=None):
#     with SessionManager() as db_session:
#         response = common_handler.handle_error(local_code_crud.get_local_codes_by_mfo, mfo_id, db_session)
#     return response

@router.post('/v1/create')
def local_code_create(request: LocalCode):
    with SessionManager() as db_session:
        response = common_handler.handle_error(local_code_crud.create_local_code, request, db_session)
    return response



@router.put('/v1/update/{id}')
def local_code_update(id:int, request: LocalCode):
    with SessionManager() as db_session:
        response = common_handler.handle_error(local_code_crud.update_local_code, id, request, db_session)
    return response


@router.delete('/v1/delete/{id}')
def local_code_delete(id:int):
    with SessionManager() as db_session:
        response = common_handler.handle_error(local_code_crud.delete_local_code, id, db_session)
    return response