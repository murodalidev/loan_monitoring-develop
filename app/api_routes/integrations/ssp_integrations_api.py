from fastapi import APIRouter, Depends, UploadFile, Body
from typing import List
from app.db.connect_db import SessionManager
from ...services.loan_monitoring.integrations import ssp_integrations
from ...config.logs_config import info_logger
from app.middleware.auth_file import AuthHandler
from ...schemas.integrations import SSP_integrations
from ...common.save_file import save_multiple_files
auth_handler = AuthHandler()



router = APIRouter(
    prefix = "/integrations/ssp", tags=["SSP"]
)

@router.get('/v1/theme-list')
def ssp_theme_list(user=Depends(auth_handler.auth_wrapper)):
    response = ssp_integrations.ssp_theme_list()
    info_logger.info("User %s requested ssp_theme_list", user.id)
    return response


@router.get('/v1/organization-list')
def ssp_organization_list(user=Depends(auth_handler.auth_wrapper)):
    response = ssp_integrations.ssp_organization_list()
    info_logger.info("User %s requested ssp_organization_list", user.id)
    return response


@router.get('/v1/claim-list')
def ssp_claim_list(user=Depends(auth_handler.auth_wrapper)):
    response = ssp_integrations.ssp_claim_list()
    info_logger.info("User %s requested ssp_claim_list", user.id)
    return response


@router.get('/v1/currency-list')
def ssp_currency_list(user=Depends(auth_handler.auth_wrapper)):
    response = ssp_integrations.ssp_currency_list()
    info_logger.info("User %s requested ssp_currency_list", user.id)
    return response


@router.get('/v1/claim-application')
def ssp_claim_application(user=Depends(auth_handler.auth_wrapper)):
    response = ssp_integrations.ssp_claim_application_get()
    info_logger.info("User %s requested ssp_claim_application", user.id)
    return response


@router.get('/v1/language-list')
def ssp_language_list(user=Depends(auth_handler.auth_wrapper)):
    response = ssp_integrations.ssp_language_list()
    info_logger.info("User %s requested ssp_language_list", user.id)
    return response


@router.get('/v1/integration/{id}')
def ssp_integration(id:int, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = ssp_integrations.ssp_integration(id, user.id, db_session)
    info_logger.info("User %s requested ssp_integration", user.id)
    return response


@router.get('/v1/requests-by-loan/{id}')
def ssp_theme_list(id:int,user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = ssp_integrations.get_requests_by_loan(id, db_session)
    info_logger.info("User %s requested ssp_theme_list", user.id)
    return response


@router.post('/v1/claim-aplication')
def ssp_theme_list(request:SSP_integrations = Body(...), copy_loan_agreement: UploadFile = None, warning_letter_or_requirement: UploadFile = None,
                    copy_return_schedule: UploadFile = None, copy_credit_application: UploadFile = None, copy_pledge_surety: UploadFile = None,
                    copy_passport_if_entity: UploadFile = None, copy_postal_receipt: UploadFile = None,ssp_membership: UploadFile = None,
                    other_files: List[UploadFile] = None, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        file_path = save_multiple_files(directory='ssp_files', copy_loan_agreement = copy_loan_agreement, warning_letter_or_requirement = warning_letter_or_requirement, 
                                        copy_return_schedule = copy_return_schedule, copy_credit_application = copy_credit_application, 
                                        copy_pledge_surety = copy_pledge_surety, copy_passport_if_entity = copy_passport_if_entity, 
                                        copy_postal_receipt = copy_postal_receipt, ssp_membership = ssp_membership, other_files=other_files)
        response = ssp_integrations.ssp_claim_application_post(request, user.id, file_path, db_session)
    info_logger.info("User %s requested ssp_theme_list", user.id)
    return response


@router.get('/v1/get-post-data')
def get_post_data(loan_portfolio_id:int):
    with SessionManager() as db_session:
        response = ssp_integrations.get_data_for_post(loan_portfolio_id, db_session)
    # info_logger.info("User %s requested get_data_for_post", user.id)
    return response