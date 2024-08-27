from fastapi import APIRouter, Depends
from app.db.connect_db import SessionManager
from ...services.loan_monitoring.integrations import adliya_integrations
from ...config.logs_config import info_logger
from app.middleware.auth_file import AuthHandler
from ...schemas.integrations import Adliya_lifting_ban_imposed_by_bank, Adliya_lifting_ban_imposed_by_notary

auth_handler = AuthHandler()



router = APIRouter(
    prefix = "/integrations/adliya", tags=["Adliya API"]
)

@router.post('/v1/lifting-ban/bank')
def lifting_ban_imposed_by_bank(request: Adliya_lifting_ban_imposed_by_bank, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = adliya_integrations.adliya_lifting_ban_imposed_by_bank(request, user.id, db_session)
    info_logger.info("User %s requested adliya_lifting_ban_imposed_by_bank", user.id)
    return response


@router.post('/v1/lifting-ban/notary')
def lifting_ban_imposed_by_notary(request: Adliya_lifting_ban_imposed_by_notary, user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = adliya_integrations.adliya_lifting_ban_imposed_by_notary(request, user.id, db_session)
    info_logger.info("User %s requested adliya_lifting_ban_imposed_by_notary", user.id)
    return response


@router.get('/v1/personal-document-type')
def adliya_personal_document_type(user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = adliya_integrations.adliya_personal_document_type(user.id, db_session)
    info_logger.info("User %s requested adliya_personal_document_type", user.id)
    return response


@router.get('/v1/org-type')
def adliya_org_type(user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = adliya_integrations.adliya_org_type(user.id, db_session)
    info_logger.info("User %s requested adliya_org_type", user.id)
    return response


@router.get('/v1/subject-type')
def adliya_subject_type(user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = adliya_integrations.adliya_subject_type(user.id, db_session)
    info_logger.info("User %s requested adliya_subject_type", user.id)
    return response


@router.get('/v1/post-info')
def adliya_post_info(user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = adliya_integrations.adliya_post_info(user.id, db_session)
    info_logger.info("User %s requested adliya_post_info", user.id)
    return response


@router.get('/v1/doc-type')
def adliya_doc_type(user=Depends(auth_handler.auth_wrapper)):
    with SessionManager() as db_session:
        response = adliya_integrations.adliya_doc_type(user.id, db_session)
    info_logger.info("User %s requested adliya_doc_type", user.id)
    return response