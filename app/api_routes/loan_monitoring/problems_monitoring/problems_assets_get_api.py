from fastapi import APIRouter,Body, UploadFile, File, Depends
from ....services.loan_monitoring.problems_case.problems_assets.take_to_bank_balance import send_results, accept_and_send_to_lawyer, get_problems_assets, send_files_lawyer, get_problems_assets_for_lawyer
from app.db.connect_db import SessionManager
from typing import  List, Optional
from ....services.websocket.create_websocket import manager
import json
from ....common.save_file import save_file, save_multiple_files
from ....schemas.problems_case_schemas import ProblemsAssetsSendResults, ProblemsAssetsAcceptOrRework, ProblemsAssetsLawyerSendResult
from app.middleware.auth_file import AuthHandler
auth_handler = AuthHandler()
import logging
logger = logging.getLogger(__name__)
from typing_extensions import Annotated

router = APIRouter(
    prefix = "/problems-case/assets", tags=["Problems Assets"]
)


@router.post('/get/v1/send-results')
async def send_problems_assets_results(request:ProblemsAssetsSendResults= Body(...), regional_office_letter: UploadFile = None,loan_agreement: UploadFile = None,
                                       regional_protocol: UploadFile = None,warning_letter: UploadFile = None,application_form: UploadFile = None,
                                       courts_decision: UploadFile = None,performance_list: UploadFile = None,mib_offer_letter: UploadFile = None,
                                       brief_description_problem: UploadFile = None,regional_lawyer_conclusion: UploadFile = None,cadastre_technical_passport: UploadFile = None,
                                       independent_assessment: UploadFile = None,bank_and_client_agreement: UploadFile = None, pledge_agreement: UploadFile = None, pledge_photos: UploadFile = None,
                                       letter_of_acceptance_mib: UploadFile = None,prohibition_except_for_bank: UploadFile = None,head_region_guarant_lettter: UploadFile = None,
                                       collateral_monitoring_document: UploadFile = None,passport: UploadFile = None,other_files: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='problems_assets_files', regional_office_letter = regional_office_letter, loan_agreement = loan_agreement, regional_protocol = regional_protocol, 
                                        warning_letter = warning_letter, application_form = application_form, courts_decision = courts_decision, performance_list = performance_list, 
                                        mib_offer_letter = mib_offer_letter, brief_description_problem = brief_description_problem, regional_lawyer_conclusion = regional_lawyer_conclusion,
                                        cadastre_technical_passport = cadastre_technical_passport, independent_assessment = independent_assessment,
                                        bank_and_client_agreement = bank_and_client_agreement, pledge_agreement = pledge_agreement,pledge_photos = pledge_photos,
                                        letter_of_acceptance_mib = letter_of_acceptance_mib, prohibition_except_for_bank = prohibition_except_for_bank,
                                        head_region_guarant_lettter = head_region_guarant_lettter, collateral_monitoring_document = collateral_monitoring_document, 
                                        passport = passport, other_files = other_files,)
        response = send_results.upload_problems_assets_files(request, file_path, db_session)
        message = {'notification_message':'upload results', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response




@router.post('/get/v1/lawyer-send-results')
async def send_problems_assets_results(request:ProblemsAssetsLawyerSendResult= Body(...), lawyers_conclusion: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='problems_assets_files', lawyers_conclusion = lawyers_conclusion)
        response = send_files_lawyer.upload_problems_assets_lawyer_decision_file(request, file_path, db_session)
        message = {'notification_message':'upload results', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response



@router.post('/get/v1/accept-or-rework')
async def accept_or_rework_problems_assets(request:ProblemsAssetsAcceptOrRework):
    with SessionManager() as db_session:
        response = accept_and_send_to_lawyer.accept_or_rework_problems_assets_data(request, db_session)
        message = {'notification_message':'accept or rework', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response






@router.post('/get/v1/send-decision')
def send_problems_assets_results(request:ProblemsAssetsLawyerSendResult= Body(...), credit_committee_decision: UploadFile = None):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='problems_assets_files', credit_committee_decision = credit_committee_decision)
        response = send_results.upload_problems_assets_decision(request, file_path, db_session)
    return response






@router.get('/get/v1/get-details')
def get_problems_asset(problem_case_id:int, problems_assets_type_id:int):
    with SessionManager() as db_session:
        response = get_problems_assets.get_problems_assets_details(problem_case_id, problems_assets_type_id, db_session)
    return response



@router.get('/get/v1/for-lawyer')
def problems_case(size:int, page:int, region_id:int=None, local_code_id:int=None, loan_id:int=None, client_name:str=None, 
               is_target:int=None, product_type:int=None, client_type:str=None, total_overdue_asc_desc:int=None, client_code:int=None, expired:bool=None,
               second_responsible:int=None,
               user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        db_session.add(user)
        response = get_problems_assets_for_lawyer.get_all_problems_assets_for_lawyer(size, page, region_id, local_code_id, loan_id, client_name, is_target,
                                                    product_type, client_type, client_code, total_overdue_asc_desc, user, second_responsible,
                                                    user.department, db_session)
    return response