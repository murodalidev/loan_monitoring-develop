from fastapi import APIRouter,Body, UploadFile, File
from ....services.loan_monitoring.problems_case.problems_assets.sell import get_problems_assets_sell, send_results, accept_or_rework
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


@router.post('/sell/v1/send-results')
async def send_problems_assets_sell_results(request:ProblemsAssetsSendResults= Body(...), cadastre_passport_in_bank: UploadFile = None, copy_cadastre_passport: UploadFile = None,
                                        e_rating: UploadFile = None, cadastre_passport_old: UploadFile = None, certificate_of_acceptance_mib: UploadFile = None,
                                        costs_for_purchasing: UploadFile = None, real_estate_photos: UploadFile = None, regional_office_letter: UploadFile = None,
                                        regional_protocol: UploadFile = None, courts_decision: UploadFile = None, other_files: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='problems_assets_files', cadastre_passport_in_bank = cadastre_passport_in_bank, copy_cadastre_passport = copy_cadastre_passport,
                                        e_rating = e_rating, cadastre_passport_old = cadastre_passport_old, certificate_of_acceptance_mib = certificate_of_acceptance_mib,
                                        costs_for_purchasing = costs_for_purchasing, real_estate_photos = real_estate_photos, regional_office_letter = regional_office_letter,
                                        regional_protocol = regional_protocol, courts_decision = courts_decision, other_files = other_files)
        response = send_results.upload_problems_assets_sell_files(request, file_path, db_session)
        message = {'notification_message':'upload results', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response




@router.post('/sell/v1/accept-or-rework')
async def accept_or_rework_problems_assets_sell(request:ProblemsAssetsAcceptOrRework):
    with SessionManager() as db_session:
        response = accept_or_rework.accept_or_rework_problems_assets_sell_data(request, db_session)
        message = {'notification_message':'accept or rework', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response



@router.post('/sell/v1/send-decision')
async def send_problems_assets_sell_decision(request:ProblemsAssetsLawyerSendResult= Body(...), credit_committee_decision: List[UploadFile] = None):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='problems_assets_files', credit_committee_decision = credit_committee_decision)
        response = send_results.upload_problems_assets_sell_decision(request, file_path, db_session)
        message = {'notification_message':'upload results', 'type':'juridical'}
        await manager.send_direct_message(request.to_user,json.dumps(message))
    return response






@router.get('/sell/v1/get-details')
def get_problems_asset_sell(problem_case_id:int, problems_assets_type_id:int):
    with SessionManager() as db_session:
        response = get_problems_assets_sell.get_problems_assets_sell_details(problem_case_id, problems_assets_type_id, db_session)
    return response
