from fastapi import APIRouter, Depends, UploadFile, Body
from app.db.connect_db import SessionManager
from typing import Union, List
from ....services.websocket.create_websocket import manager
import json
from ....common.save_file import save_file, save_multiple_files
from ....services.loan_monitoring.monitoring_case import deadline_extension_request
from ....services.loan_monitoring.monitoring_case import monitoring_templates
from ....schemas.deadline_extension_schemas import  DeadlineExtension, AcceptOrDeclineExtension
from app.middleware.auth_file import AuthHandler

auth_handler = AuthHandler()


router = APIRouter(
    prefix = "/deadline-extension", tags=["Deadline Extension"]
)



@router.post('/v1/request')
async def deadline_extension(request: DeadlineExtension= Body(...), extension_files: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='deadline_extention_files',extension_files=extension_files)
        
        response = deadline_extension_request.request_extension(request, file_path, db_session)
        message = {'notification_message':'send to check extension request', 'type':'monitoring'}
        await manager.send_direct_message(request.to_user_id, json.dumps(message))
    return response


@router.put('/v2/accept-or-decline')
async def extension_accep_or_decline(request:AcceptOrDeclineExtension):
    with SessionManager() as db_session:
        response = deadline_extension_request.accept_or_decline_extension(request, db_session)
        message = {'notification_message':'accept or rework extension', 'type':'target'}
        await manager.send_direct_message(request.to_user, json.dumps(message))
    return response




@router.get('/v2/get')
async def extension_get(loan_case_id:int = None, case_type:int=None):
    with SessionManager() as db_session:
        response = deadline_extension_request.get_case_deadline_extension(loan_case_id, case_type, db_session)
        
    return response

@router.get('/v2/get-history')
async def extension_get(loan_case_id:int = None, case_type:int=None):
    with SessionManager() as db_session:
        response = deadline_extension_request.get_case_deadline_extension_history(loan_case_id, case_type, db_session)
        
    return response



@router.get('/v2/get/case-type')
async def extension_get():
    with SessionManager() as db_session:
        response = deadline_extension_request.get_case_hitory_type(db_session)
        
    return response