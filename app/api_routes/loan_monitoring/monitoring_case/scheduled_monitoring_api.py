from fastapi import APIRouter,  UploadFile, Body
from app.db.connect_db import SessionManager
from typing import List
from ....services.websocket.create_websocket import manager
import json
from ....common import common_handler
from fastapi import BackgroundTasks
from ....common.save_file import save_file, save_multiple_files
from ....services.loan_monitoring.monitoring_case import scheduled_monitoring_crud, scheduled_history_crud
from ....schemas.monitoring_case_schemas import AcceptOrReworkScheduledMonitoring, TargetMonitoringCheck, ScheduledMonitoringCheck

router = APIRouter(
    prefix = "/monitoring-case/scheduled-monitoring", tags=["Monitoring Case"]
)


@router.get('/v1/get/all')
def portrfolio(monitoring_id:int):
    with SessionManager() as db_session:
        response = common_handler.handle_error(scheduled_monitoring_crud.get_all_scheduled_monitoring, monitoring_id, db_session)
    return response


@router.post('/v1/send-to-check')
async def portrfolio(request: ScheduledMonitoringCheck= Body(...), monitoring_act: UploadFile = None, statement: UploadFile = None, business_plan: UploadFile = None,
                     passport: UploadFile = None, letter_of_attorney: UploadFile = None, sign_example: UploadFile = None,
                     loan_agreement: UploadFile = None, balance_sheet: UploadFile = None, auditors_report: UploadFile = None,
                     security_documents: UploadFile = None, credit_comission_protocol: UploadFile = None, photo: List[UploadFile] = None, other_files: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='scheduled_files', monitoring_act=monitoring_act, statement=statement, business_plan=business_plan, passport=passport, letter_of_attorney=letter_of_attorney,
                                        sign_example=sign_example, loan_agreement=loan_agreement, balance_sheet=balance_sheet, auditors_report=auditors_report, security_documents=security_documents,
                                        credit_comission_protocol=credit_comission_protocol, photo=photo, other_files=other_files)
        response = common_handler.handle_error(scheduled_monitoring_crud.upload_file_send_scheduled_results, request, file_path, db_session)
        
        message = {'notification_message':'send to check schedule', 'type':'schedule'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response



@router.post('/v2/send-to-check')
async def portrfolio(request: ScheduledMonitoringCheck= Body(...), files: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = [save_file(file) for file in files]
        response = scheduled_monitoring_crud.upload_file_send_scheduled_resultsv2(request, file_path, db_session)
        message = {'notification_message':'send to check schedule', 'type':'schedule'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response


@router.post('/v1/accept-or-rework')
async def portrfolio(request:AcceptOrReworkScheduledMonitoring):
    with SessionManager() as db_session:
        response = common_handler.handle_error(scheduled_monitoring_crud.accept__or_rework_scheduled_monitoring, request, db_session)
        
        message = {'notification_message':'accept or rework', 'type':'schedule'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response

@router.post('/v2/accept-or-rework')
async def portrfolio(request:AcceptOrReworkScheduledMonitoring):
    with SessionManager() as db_session:
        response = scheduled_monitoring_crud.accept_or_rework_scheduled_monitoringv2(request, db_session)
        message = {'notification_message':'accept or rework', 'type':'schedule'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response



@router.get('/v1/frequency-period/getall')
def portrfolio():
    with SessionManager() as db_session:
        response = common_handler.handle_error(scheduled_monitoring_crud.get_frequency_periods, db_session)
    return response

@router.get('/v1/get/history')
def portrfolio(monitoring_id:int = None):
    with SessionManager() as db_session:
        response = common_handler.handle_error(scheduled_history_crud.get_scheduled_history, monitoring_id, db_session)
    return response




