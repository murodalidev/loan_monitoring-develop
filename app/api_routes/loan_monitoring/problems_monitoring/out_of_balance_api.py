from fastapi import APIRouter,Body, UploadFile, File, Depends
from ....services.loan_monitoring.problems_case.problems_assets.take_to_out_of_balance import get_out_of_balance_for_lawyer, accept_and_send_to_lawyer, send_files_lawyer, send_results
from ....services.loan_monitoring.problems_case.problems_assets.take_to_bank_balance import get_problems_assets
from ....services.loan_monitoring.problems_case.problems_assets.take_to_out_of_balance import get_out_of_balance_for_lawyer
from app.db.connect_db import SessionManager
from typing import  List, Optional
from ....services.websocket.create_websocket import manager
import json
from ....common.save_file import save_file, save_multiple_files
from ....schemas.problems_case_schemas import OutOfBalanceAcceptOrRework, ProblemsAssetsAcceptOrRework, ProblemsAssetsLawyerSendResult, OutOfBalanceSendResults, OutOfBalanceLawyerSendResult
from app.middleware.auth_file import AuthHandler
auth_handler = AuthHandler()
import logging
logger = logging.getLogger(__name__)
from typing_extensions import Annotated

router = APIRouter(
    prefix = "/problems-case/out-of-balance", tags=["Problems Assets"]
)


@router.post('/v1/send-results')
async def send_out_of_balance_results(request:OutOfBalanceSendResults= Body(...),certificate_passport:UploadFile = None, documents_confirming_loan: UploadFile = None, commission_statement: UploadFile = None,
                                        all_monitoring_files: UploadFile = None, loan_agreement_schedule: UploadFile = None, sales_service_invoices: UploadFile = None,
                                        measures_banks_lawyer: UploadFile = None, conclusion_transfer_to_95413: UploadFile = None,
                                        statement: UploadFile = None, other_files: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='out_of_balance_files', certificate_passport = certificate_passport, documents_confirming_loan = documents_confirming_loan,
                                        commission_statement = commission_statement, all_monitoring_files = all_monitoring_files, loan_agreement_schedule = loan_agreement_schedule, \
                                        sales_service_invoices = sales_service_invoices, measures_banks_lawyer = measures_banks_lawyer, conclusion_transfer_to_95413 = conclusion_transfer_to_95413, 
                                         statement = statement, other_files = other_files,)
        response = send_results.upload_out_of_balance_files(request, file_path, db_session)
        message = {'notification_message':'upload results', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response




@router.post('/v1/lawyer-send-results')
async def send_problems_assets_results(request:OutOfBalanceLawyerSendResult= Body(...), lawyers_conclusion: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='out_of_balance_files', lawyers_conclusion = lawyers_conclusion)
        response = send_files_lawyer.upload_out_of_balance_lawyer_decision_file(request, file_path, db_session)
        message = {'notification_message':'upload results', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response



@router.post('/v1/accept-or-rework')
async def accept_or_rework_problems_assets(request:OutOfBalanceAcceptOrRework):
    with SessionManager() as db_session:
        response = accept_and_send_to_lawyer.accept_or_rework_out_of_balance_data(request, db_session)
        message = {'notification_message':'accept or rework', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response






@router.post('/v1/send-decision')
def send_problems_assets_results(request:OutOfBalanceLawyerSendResult= Body(...), credit_committee_decision: UploadFile = None):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='out_of_balance_files', credit_committee_decision = credit_committee_decision)
        response = send_results.upload_out_of_balance_decision(request, file_path, db_session)
    return response






@router.get('/v1/get-details')
def get_problems_asset(problem_case_id:int):
    with SessionManager() as db_session:
        response = get_out_of_balance_for_lawyer.get_out_of_balance_details(problem_case_id, db_session)
    return response



@router.get('/v1/for-lawyer')
def problems_case(size:int, page:int, region_id:int=None, local_code_id:int=None, loan_id:int=None, client_name:str=None, 
               is_target:int=None, product_type:int=None, client_type:str=None, total_overdue_asc_desc:int=None, client_code:int=None, expired:bool=None,
               second_responsible:int=None,
               user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = get_out_of_balance_for_lawyer.get_all_out_of_balance_for_lawyer(size, page, region_id, local_code_id, loan_id, client_name, is_target,
                                                    product_type, client_type, client_code, total_overdue_asc_desc, user, second_responsible,
                                                    user.department, db_session)
    return response