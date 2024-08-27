from fastapi import APIRouter, Depends, UploadFile, Body, HTTPException
from app.db.connect_db import SessionManager
from typing import Union, List
from ....services.websocket.create_websocket import manager
import json
from ....common.save_file import save_file, save_multiple_files
from ....common import common_handler
from ....services.loan_monitoring.monitoring_case import target_monitoring_crud, target_history_crud
from ....services.loan_monitoring.monitoring_case import monitoring_templates

from ....schemas.monitoring_case_schemas import AcceptOrReworkTargetMonitoring, TargetMonitoringCheck, TargetTemplate

router = APIRouter(
    prefix = "/monitoring-case/target-monitoring", tags=["Monitoring Case"]
)


@router.get('/v1/get/detail')
def portrfolio(target_monitoring_id:int):
    with SessionManager() as db_session:
        response = common_handler.handle_error(target_monitoring_crud.get_target_monitoring, target_monitoring_id, db_session)
    return response


@router.get('/v1/get/for-problem')
def portrfolio(monitoring_case_id:int):
    with SessionManager() as db_session:
        response = common_handler.handle_error(target_monitoring_crud.get_target_monitoring_for_problem, monitoring_case_id, db_session)
    return response

@router.post('/v1/accept-or-rework')
async def portrfolio(request:AcceptOrReworkTargetMonitoring):
    with SessionManager() as db_session:
        response = target_monitoring_crud.accept__or_rework_target_monitoring(request, db_session)
        
        message = {'notification_message':'accept or rework target', 'type':'target'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response


@router.post('/v2/accept-or-rework')
async def portrfolio(request:AcceptOrReworkTargetMonitoring):
    with SessionManager() as db_session:
        response = common_handler.handle_error(target_monitoring_crud.accept__or_rework_target_monitoringv2, request, db_session)
        
        message = {'notification_message':'accept or rework target', 'type':'target'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response



@router.post('/v1/send-to-check')
async def portrfolio(request: TargetMonitoringCheck= Body(...),
                     target_act: UploadFile = None, statement: UploadFile = None, business_plan: UploadFile = None,
                     passport: UploadFile = None, letter_of_attorney: UploadFile = None, sign_example: UploadFile = None,
                     loan_agreement: UploadFile = None, balance_sheet: UploadFile = None, auditors_report: UploadFile = None,
                     security_documents: UploadFile = None, contract_of_sale:UploadFile = None, credit_comission_protocol: UploadFile = None, invoice: List[UploadFile] = None,
                     photo: List[UploadFile] = None, other_files: List[UploadFile] = None):
    
    with SessionManager() as db_session:
        
        file_path = save_multiple_files(directory='target_files',target_act=target_act, statement=statement, business_plan=business_plan, passport=passport, letter_of_attorney=letter_of_attorney,
                                        sign_example=sign_example, loan_agreement=loan_agreement, contract_of_sale=contract_of_sale, balance_sheet=balance_sheet, auditors_report=auditors_report, security_documents=security_documents,
                                        credit_comission_protocol=credit_comission_protocol, invoice=invoice, photo=photo, other_files=other_files)
        response = common_handler.handle_error(target_monitoring_crud.upload_file_send_target_results, request, file_path, db_session)
        
        message = {'notification_message':'send to check target', 'type':'target'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response


@router.post('/v2/send-to-check')
async def portrfolio(request: TargetMonitoringCheck= Body(...), files: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = [save_file(file) for file in files]
        response = target_monitoring_crud.upload_file_send_target_resultsv2(request, file_path, db_session)
        message = {'notification_message':'send to check target', 'type':'target'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response

@router.get('/v1/get/target-results')
def portrfolio():
    with SessionManager() as db_session:
        response = common_handler.handle_error(target_monitoring_crud.get_target_monitoring_results, db_session)
    return response



@router.post('/v1/get/target-template')
def get_template(request:TargetTemplate):
    with SessionManager() as db_session:
        response = common_handler.handle_error(monitoring_templates.getTemplate, request, db_session)
    return response



@router.get('/v1/get/history')
def portrfolio(target_id:int = None):
    with SessionManager() as db_session:
        response = common_handler.handle_error(target_history_crud.get_target_history, target_id, db_session)
    return response





@router.get('/v1/reset')
def portrfolio(loan_case_id:int = None):
    with SessionManager() as db_session:
        response = target_monitoring_crud.reset_target_monitoring(loan_case_id, db_session)
    return response
