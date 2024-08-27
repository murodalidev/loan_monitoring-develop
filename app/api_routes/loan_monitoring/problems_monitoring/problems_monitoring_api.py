from fastapi import APIRouter, Depends, UploadFile, Body
from ....services.loan_monitoring.monitoring_case import target_monitoring_crud
from ....services.loan_monitoring.monitoring_case import scheduled_monitoring_crud
from ....services.loan_monitoring.problems_case.problems_monitoring import appoint_problems_monitoring, upload_problems_monitoring_results, accept_or_rework_problems_monitoring, get_problems_monitoring
from ....services.loan_monitoring.juridical_case import juridical_case_crud
from app.db.connect_db import SessionManager
from typing import Union, List
from ....services.websocket.create_websocket import manager
import json
from ....common.save_file import save_file, save_multiple_files
from app.middleware.auth_file import AuthHandler
auth_handler = AuthHandler()
from ....common import common_handler
from ....services.loan_monitoring.loan_case import loan_case_crud
from ....schemas.problems_case_schemas import ProblemsCaseSend, ReplyToNewLoan
from ....schemas.problems_case_schemas import ProblemsMonitoringAppoint, ProblemsMonitoringSendResults, AcceptOrReworkProblemsMonitoring
router = APIRouter(
    prefix = "/problems-monitoring", tags=["Problems Monitoring"]
)



@router.get('/v1/get')
def get_problems(problems_case_id:int):
    with SessionManager() as db_session:
        response = common_handler.handle_error(get_problems_monitoring.get_all_problems_monitoring, problems_case_id, db_session)
    return response


@router.get('/v1/get/details')
def get_problems_details(problems_case_id:int, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = get_problems_monitoring.get_problems_case_details(problems_case_id, db_session)
    return {"loan_case_details":response}



@router.post('/v1/appoint-monitoring')
async def appoint_monitoring(request:ProblemsMonitoringAppoint):
    with SessionManager() as db_session:
        response = appoint_problems_monitoring.appoint_problems_monitoring(request,db_session)
        message = {'notification_message':'appoint problems monitoring', 'type':'problem'}
        await manager.send_direct_message(request.second_responsible_id,json.dumps(message))
    return response


@router.post('/v1/send-results')
async def send_results(request:ProblemsMonitoringSendResults= Body(...), problems_files: List[UploadFile] = None, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='problems_monitoring_files', problems_files = problems_files)
        db_session.add(user)
        upload_problems_monitoring_results.upload_file_send_problems_results(request, file_path, db_session)
        message = {'notification_message':'send results', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return 'OK'



@router.post('/v1/accept-or-rework')
async def accept_or_rework_problem_monitoring(request:AcceptOrReworkProblemsMonitoring):
    with SessionManager() as db_session:
        response = accept_or_rework_problems_monitoring.accept_or_rework_problems_monitoring(request, db_session)
        message = {'notification_message':'accept or rework', 'type':'unschedule'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response





# @router.get('/v1/get/all')
# def portrfolio(user=Depends(auth_handler.auth_wrapper)):
#     with SessionManager() as db_session:
#         db_session.add(user)
#         response = problems_case_crud.get_all_problems_case(user.id, db_session)
#     return {"loan_case":response}








