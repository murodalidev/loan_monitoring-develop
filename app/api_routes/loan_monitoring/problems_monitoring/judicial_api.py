from fastapi import APIRouter,Body, UploadFile, File
from ....services.loan_monitoring.problems_case.judicial_process import send_results, accept_or_rework_judicial_data, get_judicial_data
from app.db.connect_db import SessionManager
from typing import  List, Optional
from ....services.websocket.create_websocket import manager
import json
from ....common import common_handler
from ....common.save_file import save_file, save_multiple_files
from ....schemas.juridical_case_schemas import JudicialSendResults, AcceptOrReworkJudicialData, JudicialAuthorityCrud
from app.middleware.auth_file import AuthHandler
auth_handler = AuthHandler()
import logging
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix = "/problems-case/judicial", tags=["Judicial"]
)




@router.post('/v1/send-results')
async def judicial_send_results(request:JudicialSendResults= Body(...), judicial_files: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='judicial_files', judicial_files = judicial_files)
        response = send_results.upload_judicial_results(request, file_path, db_session)
        message = {'notification_message':'upload results', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response



@router.post('/v1/accept-or-rework')
async def accept_or_rework_judicial(request:AcceptOrReworkJudicialData):
    with SessionManager() as db_session:
        response = accept_or_rework_judicial_data.accept_or_rework_judicial_data(request, db_session)
        message = {'notification_message':'accept or rework', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response



@router.get('/v1/get-data')
def get_judicial(problem_case_id:int, judicial_type_id:int, authority_id:int):
    
    with SessionManager() as db_session:
        response = get_judicial_data.get_judicial_details(problem_case_id, judicial_type_id, authority_id, db_session)
    return response


@router.get('/v1/authority/get')
def get_authority(region_id:int, authority_type_id:int):
    with SessionManager() as db_session:
        response = get_judicial_data.get_judicial_authorities(region_id, authority_type_id, db_session)
    return response




@router.get('/v1/all-existing/get')
def get_all_existing(problem_case_id:int):
    with SessionManager() as db_session:
        response = get_judicial_data.get_judicial_all_existing(problem_case_id, db_session)
    return response







@router.get('/v1/authority/read/all')
def authority_read_all(name:str=None, region_id:int=None, type_id:int=None, code:str=None, page:int=None, size:int=None):
    with SessionManager() as db_session:
        response = common_handler.handle_error(get_judicial_data.get_all_judicial_authorities, name, region_id, type_id, code, page, size, db_session)
    return response

@router.get('/v1/authority/data-for-create/get')
def get_authority_type():
    with SessionManager() as db_session:
        response = common_handler.handle_error(get_judicial_data.get_judicial_authority_type, db_session)
    return response


@router.get('/v1/authority/get-one')
def get_authority_type(judicial_authority_id:int):
    with SessionManager() as db_session:
        response = common_handler.handle_error(get_judicial_data.get_one_judicial_authority, judicial_authority_id, db_session)
    return response




@router.post('/v1/create')
def authority_create(request: JudicialAuthorityCrud):
    with SessionManager() as db_session:
        response = common_handler.handle_error(get_judicial_data.create_judicial_authority, request, db_session)
    return response



@router.put('/v1/update/{id}')
def authority_update(id:int, request: JudicialAuthorityCrud):
    with SessionManager() as db_session:
        response = common_handler.handle_error(get_judicial_data.update_judicial_authority, id, request, db_session)
    return response


@router.delete('/v1/delete/{id}')
def authority_delete(id:int):
    with SessionManager() as db_session:
        response = common_handler.handle_error(get_judicial_data.delete_judicial_authority, id, db_session)
    return response
