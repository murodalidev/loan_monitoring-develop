from fastapi import APIRouter,Body, UploadFile, File
from ....services.loan_monitoring.juridical_case import juridical_case_crud
from app.db.connect_db import SessionManager
from typing import  List, Optional
from ....services.websocket.create_websocket import manager
import json
from ....common.save_file import save_file
from ....schemas.juridical_case_schemas import JuridicalCaseAppoint, JuridicalCaseAppointTaskSchema, ReplyToNewLoan, AcceptOrRework, JuridicalCaseSendToCheck, AcceptOrReworkTask, ReturnJuridical

from app.middleware.auth_file import AuthHandler
auth_handler = AuthHandler()
import logging
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix = "/juridical-case", tags=["Juridical Case"]
)


@router.get('/v1/get/details')
def portrfolio(id:int):
    with SessionManager() as db_session:
        logger.info('User is requiring juridical case details.')
        response = juridical_case_crud.get_juridical_case_details(id,  db_session)
    return {"loan_case_details":response}





@router.post('/v1/appoint-responsible')
async def portrfolio(request:JuridicalCaseAppoint):
    with SessionManager() as db_session:
        response = juridical_case_crud.appoint_responsible_for_juridical_monitoring(request,db_session)
        message = {'notification_message':'appoint responsible', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response



@router.post('/v1/appoint-task')
async def portrfolio(request:JuridicalCaseAppointTaskSchema):
    with SessionManager() as db_session:
        response = juridical_case_crud.juridical_appoint_tasks(request,db_session)
        message = {'notification_message':'appoint task', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response

@router.post('/v1/send-to-check')
async def portrfolio(request:JuridicalCaseSendToCheck= Body(...), files: List[Optional[UploadFile]] = File(None)):
    with SessionManager() as db_session:
        file_path = [save_file(file) for file in files]
        response = juridical_case_crud.upload_file_send_results(request,file_path,db_session)
        message = {'notification_message':'send to check', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response


@router.post('/v1/accept-or-rework-task')
async def portrfolio(request:AcceptOrReworkTask):
    with SessionManager() as db_session:
        response = juridical_case_crud.acept_or_rework_task(request,db_session)
        message = {'notification_message':'accept or rework task', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response

@router.post('/v1/reply-to-new-loan')
async def portrfolio(request:ReplyToNewLoan= Body(...), files: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = [save_file(file) for file in files]
        response = juridical_case_crud.reply_to_new_juridical_case(request,file_path,db_session)
        message = {'notification_message':'reply to new loan', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response


@router.post('/v1/accept-or-rework')
async def portrfolio(request:AcceptOrRework):
    with SessionManager() as db_session:
        response = juridical_case_crud.accept_or_rework(request, db_session)
        message = {'notification_message':'accept or rework', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response

@router.post('/v1/return')
async def portrfolio(request:ReturnJuridical):
    with SessionManager() as db_session:
        response = juridical_case_crud.return_juridical(request, db_session)
        message = {'notification_message':'return loan', 'type':'juridical'}
        await manager.send_direct_message(response['to_user_id'],json.dumps(message))
    return 'OK'

@router.post('/v1/close')
async def portrfolio(request:ReturnJuridical):
    with SessionManager() as db_session:
        response = juridical_case_crud.finish_juridical(request, db_session)
        message = {'notification_message':'cloas loan', 'type':'juridical'}
        await manager.send_direct_message(response['to_user_id'],json.dumps(message))
    return response

@router.get('/v1/get/history')
def portrfolio(juridical_case_id:int, general_task_id:int):
    with SessionManager() as db_session:
        response = juridical_case_crud.get_juridical_case_history(juridical_case_id,general_task_id, db_session)
    return response



@router.get('/v1/get/intended-overdue')
def portrfolio(juridical_case_id:int, juridical_type_id:int):
    with SessionManager() as db_session:
        response = juridical_case_crud.get_juridical_intended_ocerdue(juridical_case_id,juridical_type_id, db_session)
    return response

# @router.post('/v1/appoint-scheduled-monitoring')
# def portrfolio():
#     with SessionManager() as db_session:
#         response = scheduled_monitoring_crud.appoint_scheduled_monitoring(db_session)
#     return response




# @router.post('/v1/send-to-problems')
# def portrfolio(request:ProblemsCaseSend):
#     with SessionManager() as db_session:
#         response = problems_case_crud.send_to_problems(request,db_session)
#     return response