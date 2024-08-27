from fastapi import APIRouter, Depends, UploadFile, Body
from app.db.connect_db import SessionManager
from typing import Union, List
from ....services.websocket.create_websocket import manager
import json
from ....common import common_handler
from ....common.save_file import  save_multiple_files
from ....services.loan_monitoring.monitoring_case.unscheduled_monitoring import unscheduled_monitoring_crud
from ....services.loan_monitoring.monitoring_case.unscheduled_monitoring import unscheduled_history_crud
from ....schemas.monitoring_case_schemas import AcceptOrReworkUnscheduledMonitoring, UnscheduledMonitoringAppoint, UnscheduledMonitoringCheck

router = APIRouter(
    prefix = "/unscheduled-monitoring", tags=["Unscheduled Monitoring"]
)


@router.get('/v1/get/all')
def get_unscheduled(monitoring_id:int):
    with SessionManager() as db_session:
        response = common_handler.handle_error(unscheduled_monitoring_crud.get_all_unscheduled_monitoring, monitoring_id, db_session)
    return response



@router.post('/v1/appoint')
async def appoint_unscheduled(request:UnscheduledMonitoringAppoint):
    with SessionManager() as db_session:
        response = common_handler.handle_error(unscheduled_monitoring_crud.appoint_unscheduled_monitoring, request, db_session)
        message = {'notification_message':'appoint unscheduled monitoring', 'type':'unschedule'}
        await manager.send_direct_message(request.second_responsible_id,json.dumps(message))
    return response




@router.post('/v1/send-to-check')
async def unscheduled_send_to_checks(request: UnscheduledMonitoringCheck= Body(...),uncheduled_act: UploadFile = None,
                                     statement: UploadFile = None, business_plan: UploadFile = None,
                                    passport: UploadFile = None, letter_of_attorney: UploadFile = None, sign_example: UploadFile = None,
                                    loan_agreement: UploadFile = None, balance_sheet: UploadFile = None, auditors_report: UploadFile = None,
                                    security_documents: UploadFile = None, credit_comission_protocol: UploadFile = None, photo: List[UploadFile] = None,
                                    other_files: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='unscheduled_files', uncheduled_act=uncheduled_act, statement=statement, business_plan=business_plan, passport=passport, letter_of_attorney=letter_of_attorney,
                                        sign_example=sign_example, loan_agreement=loan_agreement, balance_sheet=balance_sheet, auditors_report=auditors_report, security_documents=security_documents,
                                        credit_comission_protocol=credit_comission_protocol, photo=photo, other_files=other_files)
        response = common_handler.handle_error(unscheduled_monitoring_crud.upload_file_send_unscheduled_results,request, file_path, db_session)
        message = {'notification_message':'send to check unschedule', 'type':'unschedule'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response




@router.post('/v1/accept-or-rework')
async def accept_or_rework_unscheduled(request:AcceptOrReworkUnscheduledMonitoring):
    with SessionManager() as db_session:
        response = unscheduled_monitoring_crud.accept_or_rework_unscheduled_monitoring(request, db_session)
        message = {'notification_message':'accept or rework', 'type':'unschedule'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response




@router.get('/v1/get/history')
def unscheduled_get_history(monitoring_id:int = None):
    with SessionManager() as db_session:
        response = unscheduled_history_crud.get_unscheduled_history(monitoring_id, db_session)
    return response